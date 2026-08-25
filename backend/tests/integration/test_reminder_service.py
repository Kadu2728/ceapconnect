"""Teste de integração de `app.services.reminder_service` (lembretes automáticos).

Prova, contra um banco real, que o lembrete é enviado (notificação in-app
criada) e registrado (`ReminderLog`), e que rodar o check de novo não
reenvia o mesmo lembrete ao mesmo candidato.
"""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import CandidateProfile
from app.models.notification import Notification
from app.models.reminder_log import (
    REMINDER_DOCUMENTATION_INCOMPLETE,
    REMINDER_EXAM_7_DAYS,
    ReminderLog,
)
from app.repositories.notification_repository import NotificationRepository
from app.services import reminder_service


async def test_lembrete_de_prova_e_enviado_e_nao_reenviado(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    candidate_profile.exam_date = date.today() + timedelta(days=5)
    await db_session.flush()

    first_summary = await reminder_service.check_and_send_reminders(db_session)
    assert first_summary.candidates_checked == 1
    assert first_summary.reminders_sent >= 1

    notifications = await NotificationRepository(db_session).list_for_profile(candidate_profile.id)
    exam_notifications = [n for n in notifications if n.category == "lembretes"]
    assert len(exam_notifications) >= 1
    assert any("prova" in n.title.lower() for n in exam_notifications)

    # Rodar de novo não deve reenviar o mesmo lembrete (mesmo com a condição
    # ainda batendo — o candidato continua a 5 dias da prova).
    second_summary = await reminder_service.check_and_send_reminders(db_session)
    assert second_summary.reminders_sent == 0


async def test_lembrete_de_documentacao_pendente_respeita_o_prazo(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    # Sem nenhum documento enviado (fixture não envia nenhum) e cadastro
    # "antigo" o suficiente para passar do prazo de tolerância.
    candidate_profile.created_at = datetime.now(UTC) - timedelta(days=10)
    await db_session.flush()

    summary = await reminder_service.check_and_send_reminders(db_session)
    assert summary.reminders_sent >= 1

    stmt = select(Notification).where(Notification.candidate_profile_id == candidate_profile.id)
    notifications = (await db_session.execute(stmt)).scalars().all()
    assert any("documentação" in n.title.lower() for n in notifications)


async def test_sem_data_de_prova_nem_documento_pendente_nao_envia_nada(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    # `exam_date`/`interview_date` continuam `None` (fixture não define).
    # Documentação ainda está dentro da janela de tolerância (cadastro recente).
    summary = await reminder_service.check_and_send_reminders(db_session)
    assert summary.reminders_sent == 0


async def test_dois_candidatos_diferentes_recebem_o_mesmo_lembrete_independentemente(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """Regressão do bug óbvio de agregação em lote: o `set_sent_profile_ids`
    de um candidato não pode vazar para o outro."""
    candidate_profile.exam_date = date.today()
    await db_session.flush()

    summary = await reminder_service.check_and_send_reminders(db_session)
    assert summary.candidates_checked == 1
    assert summary.reminders_sent >= 1


async def test_reminder_type_registrado_bate_com_o_lembrete_enviado(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    candidate_profile.exam_date = date.today() + timedelta(days=6)
    candidate_profile.created_at = datetime.now(UTC) - timedelta(days=10)
    await db_session.flush()

    await reminder_service.check_and_send_reminders(db_session)

    rows = (
        (
            await db_session.execute(
                select(ReminderLog).where(ReminderLog.candidate_profile_id == candidate_profile.id)
            )
        )
        .scalars()
        .all()
    )
    reminder_types = {row.reminder_type for row in rows}
    assert REMINDER_EXAM_7_DAYS in reminder_types
    assert REMINDER_DOCUMENTATION_INCOMPLETE in reminder_types
