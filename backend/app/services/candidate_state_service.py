"""Regra de negócio do Candidate State (Candidate Journey OS — fase N1).

Ponto único de leitura do "onde este candidato está agora", para os
consumidores que precisam de mais que a barra de progresso do Dashboard:
Next Best Action (N2), Zero-Click Recovery (N3) e Modo Resgate (N4).

**Computado sob demanda, não persistido.** `RiskScore` é recalculado em lote
a cada `RISK_RECOMPUTE_INTERVAL_MINUTES` (60min por padrão) porque a fila do
coordenador tolera esse atraso; o Candidate State não pode herdar essa
cadência — "o candidato acabou de abandonar a sessão" precisa refletir no
próximo carregamento de tela, não na próxima hora. Por isso este serviço
deriva as features na hora, reaproveitando `risk_feature_service` (mesma
fonte de sinal do motor de risco, para as duas leituras nunca divergirem
sobre o mesmo candidato) em vez de esperar o job de risco passar.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.candidate_state_scoring import STATE_VERSION, classify_momentum
from app.models.candidate_document import REQUIRED_DOCUMENT_TYPES
from app.models.user import User
from app.repositories.candidate_document_repository import CandidateDocumentRepository
from app.repositories.journey_pause_repository import JourneyPauseRepository
from app.schemas.candidate_state import CandidateStateResponse, CandidateTrackableEvent
from app.schemas.journey_pause import PauseState
from app.services import activity_event_service, journey_service, risk_feature_service
from app.services.candidate_profile_service import get_profile_or_raise

_REQUIRED_DOCUMENT_COUNT = len(REQUIRED_DOCUMENT_TYPES)


async def get_candidate_state(db: AsyncSession, user: User) -> CandidateStateResponse:
    """Monta o estado computado do candidato autenticado."""
    profile = await get_profile_or_raise(db, user)

    # Mesma disciplina do Dashboard: a etapa é um valor derivado, nunca lido
    # cego da coluna (ver `journey_service`). Só commita se algo avançou.
    if await journey_service.sync_one(db, profile):
        await db.commit()

    # Lote de 1: reaproveita a mesma derivação de sinais do motor de risco
    # (batched por design) em vez de duplicar as queries de outra forma.
    features_list = await risk_feature_service.derive_features_for_group(db, [profile])
    features = features_list[0]

    doc_counts = await CandidateDocumentRepository(db).count_by_profile_ids([profile.id])
    pending_documents = max(0, _REQUIRED_DOCUMENT_COUNT - doc_counts.get(profile.id, 0))

    now = datetime.now(UTC)
    days_to_exam = None
    if profile.exam_date is not None:
        days_to_exam = (profile.exam_date - now.date()).days

    # Pausa declarada ("Jornada que Respira"): campo à parte, nunca um sexto
    # valor de `momentum`. Os cinco valores de momentum são *inferidos* de
    # comportamento; a pausa é um fato *declarado* e persistido — colapsar os
    # dois obrigaria a injetar estado de banco na classificação pura e
    # apagaria justamente a distinção que o Console de Intervenção precisa
    # ("pausou e avisou" ≠ "silenciou").
    active_pause = await JourneyPauseRepository(db).get_active_now(profile.id, now=now)

    return CandidateStateResponse(
        version=STATE_VERSION,
        computed_at=now,
        momentum=classify_momentum(features),
        current_step_key=profile.current_journey_step_key,
        days_since_last_activity=features.days_since_last_activity,
        pending_required_documents=pending_documents,
        days_to_exam=days_to_exam,
        guardian_training_overdue=features.guardian_training_overdue,
        pause=PauseState.model_validate(active_pause) if active_pause is not None else None,
    )


async def track_client_event(
    db: AsyncSession, user: User, *, name: CandidateTrackableEvent, props: dict[str, Any]
) -> None:
    """Registra um evento disparado pelo próprio cliente (clique, entrada/saída de modo).

    `name` já vem tipado como `CandidateTrackableEvent` (validado pelo
    Pydantic no schema do request) — nunca o vocabulário completo de
    `ActivityEventName`, para o candidato não conseguir gerar um evento que
    deveria ser autoritativo do servidor (ver docstring do schema).
    """
    profile = await get_profile_or_raise(db, user)
    await activity_event_service.track_committed(
        db, candidate_profile_id=profile.id, name=name, props=props
    )
