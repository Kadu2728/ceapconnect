"""Regra de negócio da Pausa Declarada ("Jornada que Respira" — fase 1).

Ponte entre a camada pura (`app.core.journey_pause_rules`) e a persistência,
no mesmo desenho de `reminder_service`/`risk_service`.

**Precedência**: uma pausa em curso suprime Next Best Action e Modo Resgate
(o produto para de cobrar avanço) e suprime a cobrança de documentação nos
lembretes — mas **nunca** os avisos de data marcada (prova, entrevista). Um
jovem que pausou porque pegou um turno extra ainda precisa saber que a prova
é amanhã; suprimir esse aviso faria a feature custar exatamente a vaga que o
produto existe para proteger.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException
from app.core.journey_pause_rules import PauseTooCloseToExamError, resolve_pause_end
from app.core.next_best_action_rules import NextBestActionInput, recommend
from app.models.activity_event import (
    EVENT_PAUSE_EXPIRED,
    EVENT_PAUSE_RESUMED,
    EVENT_PAUSE_STARTED,
)
from app.models.journey_pause import PAUSE_EXPIRED, PAUSE_RESUMED, JourneyPause
from app.models.user import User
from app.repositories.journey_pause_repository import JourneyPauseRepository
from app.schemas.journey_pause import PauseResumeResult, PauseStartRequest, PauseState
from app.services import activity_event_service, candidate_state_service
from app.services.candidate_profile_service import get_profile_or_raise

_EXAM_TOO_CLOSE_MESSAGE = (
    "Sua prova está muito perto para pausar agora — e você já chegou até aqui. "
    "Se precisar de ajuda, fale com a secretaria do CEAP."
)
_ALREADY_PAUSED_MESSAGE = "Você já tem uma pausa em andamento."


async def start_pause(db: AsyncSession, user: User, payload: PauseStartRequest) -> PauseState:
    """Inicia a pausa declarada do candidato autenticado.

    Guarda um snapshot do que ele *ia* fazer (`resume_action_key`) — a etapa
    em si não precisa ser guardada para retomada (`journey_service` é a
    autoridade sobre isso, e nunca regride), mas a recomendação vigente é
    efêmera e é ela que torna a volta de 1 toque.
    """
    profile = await get_profile_or_raise(db, user)
    repo = JourneyPauseRepository(db)

    if await repo.get_active(profile.id) is not None:
        raise ConflictException(_ALREADY_PAUSED_MESSAGE)

    started_at = datetime.now(UTC)
    try:
        ends_at = resolve_pause_end(
            started_at=started_at, requested_days=payload.days, exam_date=profile.exam_date
        )
    except PauseTooCloseToExamError as exc:
        raise BadRequestException(_EXAM_TOO_CLOSE_MESSAGE) from exc

    resume_action_key = await _snapshot_next_action_key(db, user)

    pause = await repo.create(
        candidate_profile_id=profile.id,
        started_at=started_at,
        ends_at=ends_at,
        requested_days=payload.days,
        reason_code=payload.reason_code,
        paused_at_step_key=profile.current_journey_step_key,
        resume_action_key=resume_action_key,
    )
    await activity_event_service.track(
        db,
        candidate_profile_id=profile.id,
        name=EVENT_PAUSE_STARTED,
        props={
            "requested_days": payload.days,
            "granted_days": round((ends_at - started_at).total_seconds() / 86400, 2),
            "reason_code": payload.reason_code,
            "step_key": profile.current_journey_step_key,
        },
    )
    await db.commit()

    return PauseState.model_validate(pause)


async def resume_pause(db: AsyncSession, user: User) -> PauseResumeResult:
    """Encerra a pausa em curso porque o candidato voltou por vontade própria.

    Idempotente de propósito: chamar sem pausa ativa devolve
    `resumed=False` em vez de erro — a volta tem que ser leve, e um duplo
    clique no botão "voltar" jamais deveria mostrar uma tela de erro a quem
    acabou de decidir retomar.
    """
    profile = await get_profile_or_raise(db, user)
    repo = JourneyPauseRepository(db)

    pause = await repo.get_active(profile.id)
    if pause is None:
        return PauseResumeResult(resumed=False, resume_action_key=None)

    await repo.close(pause, status=PAUSE_RESUMED, ended_at=datetime.now(UTC))
    await activity_event_service.track(
        db,
        candidate_profile_id=profile.id,
        name=EVENT_PAUSE_RESUMED,
        props={
            "days_paused": _elapsed_days(pause),
            # `True` = voltou antes do prazo acabar (sinal mais forte de
            # retomada ativa do que deixar expirar).
            "returned_early": datetime.now(UTC) < pause.ends_at,
        },
    )
    await db.commit()

    return PauseResumeResult(resumed=True, resume_action_key=pause.resume_action_key)


async def expire_due_pauses(db: AsyncSession) -> int:
    """Encerra as pausas vencidas e registra `pause_expired`. Retorna quantas.

    Roda no mesmo ciclo do job de lembretes, imediatamente antes dele: uma
    pausa vencida precisa parar de suprimir lembretes já nesta passada, e
    acoplar as duas coisas garante essa ordem sem um terceiro job disputando
    o processo único do plano free do Render.
    """
    now = datetime.now(UTC)
    repo = JourneyPauseRepository(db)
    due = await repo.list_due(now=now)
    if not due:
        return 0

    for pause in due:
        await repo.close(pause, status=PAUSE_EXPIRED, ended_at=pause.ends_at)
        await activity_event_service.track(
            db,
            candidate_profile_id=pause.candidate_profile_id,
            name=EVENT_PAUSE_EXPIRED,
            props={"days_paused": _elapsed_days(pause)},
        )

    await db.commit()
    return len(due)


async def _snapshot_next_action_key(db: AsyncSession, user: User) -> str | None:
    """A recomendação vigente no instante da pausa, sem registrar `nba_generated`.

    Usa a regra pura em vez de `next_best_action_service` de propósito: aquele
    service emite `nba_generated`, que significa "uma recomendação foi
    mostrada ao candidato". Guardar um snapshot não é mostrar nada — contar
    isso como impressão inflaria o denominador do CTR do Learning Loop.
    """
    state = await candidate_state_service.get_candidate_state(db, user)
    action = recommend(
        NextBestActionInput(
            momentum=state.momentum,
            pending_required_documents=state.pending_required_documents,
            guardian_training_overdue=state.guardian_training_overdue,
            days_to_exam=state.days_to_exam,
        )
    )
    return action.action_key if action is not None else None


def _elapsed_days(pause: JourneyPause) -> float:
    return round((datetime.now(UTC) - pause.started_at).total_seconds() / 86400, 2)
