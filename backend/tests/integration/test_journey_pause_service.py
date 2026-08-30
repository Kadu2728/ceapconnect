"""Teste de integração da Pausa Declarada ("Jornada que Respira" — fase 1).

Prova, contra um banco real, o ciclo completo (pausar → retomar / expirar) e
os dois freios que sustentam a feature: a pausa suprime cobrança de avanço,
mas **nunca** os avisos de data marcada.
"""

from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException
from app.models.activity_event import (
    EVENT_PAUSE_EXPIRED,
    EVENT_PAUSE_RESUMED,
    EVENT_PAUSE_STARTED,
    ActivityEvent,
)
from app.models.candidate_profile import CandidateProfile
from app.models.journey_pause import PAUSE_EXPIRED, PAUSE_RESUMED
from app.models.reminder_log import (
    REMINDER_DOCUMENTATION_INCOMPLETE,
    REMINDER_EXAM_1_DAY,
    ReminderLog,
)
from app.repositories.journey_pause_repository import JourneyPauseRepository
from app.repositories.user_repository import UserRepository
from app.schemas.journey_pause import PauseStartRequest
from app.services import journey_pause_service, next_best_action_service, reminder_service


def _utc_today() -> date:
    """Mesma referência de "hoje" do `reminder_service` (ver test_reminder_service)."""
    return datetime.now(UTC).date()


async def _user_of(db: AsyncSession, profile: CandidateProfile):
    user = await UserRepository(db).get_by_id(profile.user_id)
    assert user is not None
    return user


async def _event_names(db: AsyncSession, profile: CandidateProfile) -> list[str]:
    rows = await db.execute(
        select(ActivityEvent.name).where(ActivityEvent.candidate_profile_id == profile.id)
    )
    return list(rows.scalars().all())


async def test_pausar_guarda_periodo_etapa_e_emite_evento(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await _user_of(db_session, candidate_profile)

    state = await journey_pause_service.start_pause(
        db_session, user, PauseStartRequest(days=3, reason_code="trabalho")
    )

    assert state.reason_code == "trabalho"
    assert state.ends_at > datetime.now(UTC)

    pause = await JourneyPauseRepository(db_session).get_active(candidate_profile.id)
    assert pause is not None
    assert pause.requested_days == 3
    assert pause.paused_at_step_key == candidate_profile.current_journey_step_key
    assert EVENT_PAUSE_STARTED in await _event_names(db_session, candidate_profile)


async def test_pausar_duas_vezes_e_bloqueado(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """Reforça no service a mesma invariante do índice único parcial."""
    user = await _user_of(db_session, candidate_profile)
    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=3))

    with pytest.raises(ConflictException):
        await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=7))


async def test_pausar_com_prova_amanha_e_recusado(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """Perto da prova, o que o candidato precisa é aparecer — não pausar."""
    candidate_profile.exam_date = _utc_today() + timedelta(days=1)
    await db_session.flush()
    user = await _user_of(db_session, candidate_profile)

    with pytest.raises(BadRequestException):
        await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=7))


async def test_retomar_encerra_a_pausa_e_devolve_o_ponto_guardado(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await _user_of(db_session, candidate_profile)
    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=7))

    result = await journey_pause_service.resume_pause(db_session, user)

    assert result.resumed is True
    assert await JourneyPauseRepository(db_session).get_active(candidate_profile.id) is None

    history = await JourneyPauseRepository(db_session).list_for_profile(candidate_profile.id)
    assert history[0].status == PAUSE_RESUMED
    assert history[0].ended_at is not None
    assert EVENT_PAUSE_RESUMED in await _event_names(db_session, candidate_profile)


async def test_retomar_sem_pausa_ativa_nao_quebra(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """Duplo clique no botão "voltar" jamais pode virar tela de erro."""
    user = await _user_of(db_session, candidate_profile)

    result = await journey_pause_service.resume_pause(db_session, user)

    assert result.resumed is False
    assert result.resume_action_key is None


async def test_pausa_vencida_expira_e_emite_evento(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await _user_of(db_session, candidate_profile)
    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=3))

    pause = await JourneyPauseRepository(db_session).get_active(candidate_profile.id)
    assert pause is not None
    # Envelhece a pausa inteira, não só o fim: `ck_journey_pause_window`
    # (ends_at > started_at) é uma invariante real do banco e recusaria uma
    # pausa que "termina antes de começar".
    pause.started_at = datetime.now(UTC) - timedelta(days=4)
    pause.ends_at = datetime.now(UTC) - timedelta(hours=1)
    await db_session.flush()

    expired = await journey_pause_service.expire_due_pauses(db_session)

    assert expired >= 1
    history = await JourneyPauseRepository(db_session).list_for_profile(candidate_profile.id)
    assert history[0].status == PAUSE_EXPIRED
    assert EVENT_PAUSE_EXPIRED in await _event_names(db_session, candidate_profile)


async def test_pausa_vencida_nao_vale_para_o_candidato_antes_do_job_rodar(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """A leitura ignora pausa vencida por conta própria — o candidato nunca
    fica preso na experiência calma porque o job atrasou."""
    user = await _user_of(db_session, candidate_profile)
    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=3))

    pause = await JourneyPauseRepository(db_session).get_active(candidate_profile.id)
    assert pause is not None
    # Envelhece a pausa inteira, não só o fim: `ck_journey_pause_window`
    # (ends_at > started_at) é uma invariante real do banco e recusaria uma
    # pausa que "termina antes de começar".
    pause.started_at = datetime.now(UTC) - timedelta(days=4)
    pause.ends_at = datetime.now(UTC) - timedelta(hours=1)
    await db_session.flush()

    still_active = await JourneyPauseRepository(db_session).get_active_now(
        candidate_profile.id, now=datetime.now(UTC)
    )
    assert still_active is None


async def test_pausa_suprime_next_best_action(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """Recomendar durante a pausa seria cobrar de quem pediu um respiro."""
    user = await _user_of(db_session, candidate_profile)
    # Sem pausa, um candidato sem documentos recebe recomendação.
    assert await next_best_action_service.get_next_best_action(db_session, user) is not None

    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=7))

    assert await next_best_action_service.get_next_best_action(db_session, user) is None


async def test_pausa_suprime_cobranca_de_documentacao(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    candidate_profile.created_at = datetime.now(UTC) - timedelta(days=10)
    await db_session.flush()
    user = await _user_of(db_session, candidate_profile)
    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=7))

    await reminder_service.check_and_send_reminders(db_session)

    logs = await _reminder_types(db_session, candidate_profile)
    assert REMINDER_DOCUMENTATION_INCOMPLETE not in logs


async def test_pausa_nunca_suprime_aviso_de_prova(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """O freio mais importante da feature: pausar não pode custar a vaga.

    A pausa é curta o bastante para caber antes da prova (o `resolve_pause_end`
    garante a folga), e mesmo assim o aviso de "sua prova é amanhã" sai.
    """
    user = await _user_of(db_session, candidate_profile)
    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=3))

    # Prova remarcada para amanhã depois da pausa já ter começado — o caso em
    # que suprimir o aviso seria mais danoso.
    candidate_profile.exam_date = _utc_today() + timedelta(days=1)
    await db_session.flush()

    await reminder_service.check_and_send_reminders(db_session)

    assert REMINDER_EXAM_1_DAY in await _reminder_types(db_session, candidate_profile)


async def _reminder_types(db: AsyncSession, profile: CandidateProfile) -> set[str]:
    rows = await db.execute(
        select(ReminderLog.reminder_type).where(ReminderLog.candidate_profile_id == profile.id)
    )
    return set(rows.scalars().all())
