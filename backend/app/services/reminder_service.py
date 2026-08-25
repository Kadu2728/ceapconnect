"""Regra de negócio dos lembretes automáticos.

Orquestra `app.core.reminder_rules` (decide *se* um lembrete deveria disparar)
com `ReminderLog` (decide se *já disparou*) e `notification_service` (decide
*como* avisar — in-app + push, um único ponto de entrada, nenhum canal novo
criado aqui). Mesmo desenho de `risk_service.recompute_all`: percorre todos
os candidatos ativos em lote, nunca um por vez.

As três peças que tornam isso possível já existiam, ociosas, antes deste
service: o job in-process (`app.core.scheduler`, mesmo padrão do recálculo
de risco), `notification_service.create_notification` (já cria a notificação
in-app e dispara o push num único ponto) e as datas já calculadas em
`CandidateProfile` (`exam_date`, `interview_date`).
"""

import time
import uuid
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.reminder_rules import (
    should_remind_documentation_incomplete,
    should_remind_exam_1_day,
    should_remind_exam_7_days,
    should_remind_interview_1_day,
    should_remind_interview_7_days,
)
from app.models.candidate_document import REQUIRED_DOCUMENT_TYPES
from app.models.candidate_profile import CandidateProfile
from app.models.reminder_log import (
    REMINDER_DOCUMENTATION_INCOMPLETE,
    REMINDER_EXAM_1_DAY,
    REMINDER_EXAM_7_DAYS,
    REMINDER_INTERVIEW_1_DAY,
    REMINDER_INTERVIEW_7_DAYS,
    ReminderType,
)
from app.repositories.candidate_document_repository import CandidateDocumentRepository
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.reminder_log_repository import ReminderLogRepository
from app.schemas.reminder import ReminderCheckSummary
from app.services import notification_service

_REQUIRED_DOCUMENT_COUNT = len(REQUIRED_DOCUMENT_TYPES)
_ALL_REMINDER_TYPES: tuple[ReminderType, ...] = (
    REMINDER_EXAM_7_DAYS,
    REMINDER_EXAM_1_DAY,
    REMINDER_INTERVIEW_7_DAYS,
    REMINDER_INTERVIEW_1_DAY,
    REMINDER_DOCUMENTATION_INCOMPLETE,
)


async def check_and_send_reminders(db: AsyncSession) -> ReminderCheckSummary:
    """Percorre candidatos ativos e dispara os lembretes ainda não enviados."""
    started_at = time.monotonic()

    profiles = await CandidateProfileRepository(db).list_active_candidates()
    if not profiles:
        return ReminderCheckSummary(candidates_checked=0, reminders_sent=0, duration_seconds=0.0)

    profile_ids = [p.id for p in profiles]
    reminder_log_repo = ReminderLogRepository(db)
    already_sent: dict[ReminderType, set[uuid.UUID]] = {
        reminder_type: await reminder_log_repo.set_sent_profile_ids(
            profile_ids, reminder_type=reminder_type
        )
        for reminder_type in _ALL_REMINDER_TYPES
    }

    doc_counts = await CandidateDocumentRepository(db).count_by_profile_ids(profile_ids)

    today = datetime.now(UTC).date()
    sent_count = 0
    for profile in profiles:
        sent_count += await _check_profile(
            db,
            profile,
            today=today,
            uploaded_document_count=doc_counts.get(profile.id, 0),
            already_sent=already_sent,
        )

    await db.commit()

    return ReminderCheckSummary(
        candidates_checked=len(profiles),
        reminders_sent=sent_count,
        duration_seconds=round(time.monotonic() - started_at, 2),
    )


async def _check_profile(
    db: AsyncSession,
    profile: CandidateProfile,
    *,
    today: date,
    uploaded_document_count: int,
    already_sent: dict[ReminderType, set[uuid.UUID]],
) -> int:
    """Avalia e dispara os lembretes aplicáveis a um único candidato. Retorna quantos enviou."""
    sent = 0

    days_to_exam = (profile.exam_date - today).days if profile.exam_date is not None else None
    if (
        should_remind_exam_7_days(days_to_exam)
        and profile.id not in already_sent[REMINDER_EXAM_7_DAYS]
    ):
        await _send(db, profile.id, REMINDER_EXAM_7_DAYS, *_exam_reminder_content(days_to_exam))
        sent += 1
    if (
        should_remind_exam_1_day(days_to_exam)
        and profile.id not in already_sent[REMINDER_EXAM_1_DAY]
    ):
        await _send(db, profile.id, REMINDER_EXAM_1_DAY, *_exam_reminder_content(days_to_exam))
        sent += 1

    days_to_interview = (
        (profile.interview_date - today).days if profile.interview_date is not None else None
    )
    if (
        should_remind_interview_7_days(days_to_interview)
        and profile.id not in already_sent[REMINDER_INTERVIEW_7_DAYS]
    ):
        await _send(
            db,
            profile.id,
            REMINDER_INTERVIEW_7_DAYS,
            *_interview_reminder_content(days_to_interview),
        )
        sent += 1
    if (
        should_remind_interview_1_day(days_to_interview)
        and profile.id not in already_sent[REMINDER_INTERVIEW_1_DAY]
    ):
        await _send(
            db,
            profile.id,
            REMINDER_INTERVIEW_1_DAY,
            *_interview_reminder_content(days_to_interview),
        )
        sent += 1

    pending_documents = max(0, _REQUIRED_DOCUMENT_COUNT - uploaded_document_count)
    days_since_registration = (datetime.now(UTC) - profile.created_at).total_seconds() / 86400
    if (
        should_remind_documentation_incomplete(
            days_since_registration=days_since_registration, pending_documents=pending_documents
        )
        and profile.id not in already_sent[REMINDER_DOCUMENTATION_INCOMPLETE]
    ):
        await _send(
            db,
            profile.id,
            REMINDER_DOCUMENTATION_INCOMPLETE,
            *_documentation_reminder_content(pending_documents),
        )
        sent += 1

    return sent


async def _send(
    db: AsyncSession,
    candidate_profile_id: uuid.UUID,
    reminder_type: ReminderType,
    title: str,
    description: str,
) -> None:
    """Cria a notificação (in-app + push) e registra o envio — nunca as duas coisas
    separadas, para não haver como logar um envio que não aconteceu."""
    await notification_service.create_notification(
        db,
        candidate_profile_id=candidate_profile_id,
        title=title,
        description=description,
        category="lembretes",
    )
    await ReminderLogRepository(db).create(
        candidate_profile_id=candidate_profile_id, reminder_type=reminder_type
    )


def _exam_reminder_content(days_to_exam: int | None) -> tuple[str, str]:
    assert days_to_exam is not None  # noqa: S101 — só chamado depois de should_remind_exam_*
    if days_to_exam == 0:
        return "Sua prova é hoje!", "Boa sorte! Revise o que levar e o horário antes de sair."
    if days_to_exam == 1:
        return "Sua prova é amanhã", "Aproveite hoje para revisar e descansar bem à noite."
    return (
        "Sua prova está chegando",
        f"Faltam {days_to_exam} dias para sua prova. Continue se preparando!",
    )


def _interview_reminder_content(days_to_interview: int | None) -> tuple[str, str]:
    assert days_to_interview is not None  # noqa: S101
    if days_to_interview == 0:
        return (
            "Entrevista do responsável é hoje",
            "A entrevista do seu responsável com o CEAP é hoje — confirme o horário com ele(a).",
        )
    if days_to_interview == 1:
        return (
            "Entrevista do responsável é amanhã",
            "Lembre seu responsável: a entrevista com o CEAP é amanhã.",
        )
    return (
        "Entrevista do responsável se aproxima",
        f"Faltam {days_to_interview} dias para a entrevista do seu responsável com o CEAP.",
    )


def _documentation_reminder_content(pending_documents: int) -> tuple[str, str]:
    plural = "documento" if pending_documents == 1 else "documentos"
    description = (
        f"Você ainda não enviou {pending_documents} {plural} "
        "necessário(s) para avançar sua jornada."
    )
    return "Documentação pendente", description
