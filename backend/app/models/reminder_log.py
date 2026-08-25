"""Model SQLAlchemy da entidade `ReminderLog` (lembretes automáticos).

Registro **append-only** de "este lembrete já foi enviado a este candidato" —
existe só para impedir reenvio. Um lembrete nunca é reenviado depois de
registrado aqui, mesmo que a condição que o disparou continue verdadeira no
próximo ciclo do job (`reminder_service.check_and_send_reminders` roda a
cada `REMINDER_CHECK_INTERVAL_MINUTES`; sem este log, o mesmo candidato
receberia o mesmo push/notificação em todo ciclo em que a condição segue
batendo — spam, não lembrete).

Par (candidate_profile_id, reminder_type) único: é o que garante o "uma vez
só" sem precisar de nenhuma lógica adicional no service além de checar se a
linha já existe antes de enviar.
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

ReminderType = Literal[
    "exam_7_days",
    "exam_1_day",
    "interview_7_days",
    "interview_1_day",
    "documentation_incomplete",
]

REMINDER_EXAM_7_DAYS: Final = "exam_7_days"
REMINDER_EXAM_1_DAY: Final = "exam_1_day"
REMINDER_INTERVIEW_7_DAYS: Final = "interview_7_days"
REMINDER_INTERVIEW_1_DAY: Final = "interview_1_day"
REMINDER_DOCUMENTATION_INCOMPLETE: Final = "documentation_incomplete"

_VALID_REMINDER_TYPES: Final = (
    REMINDER_EXAM_7_DAYS,
    REMINDER_EXAM_1_DAY,
    REMINDER_INTERVIEW_7_DAYS,
    REMINDER_INTERVIEW_1_DAY,
    REMINDER_DOCUMENTATION_INCOMPLETE,
)


class ReminderLog(Base):
    """Prova de que um lembrete específico já foi enviado a um candidato."""

    __tablename__ = "reminder_logs"
    __table_args__ = (
        CheckConstraint(f"reminder_type IN {_VALID_REMINDER_TYPES}", name="ck_reminder_log_type"),
        UniqueConstraint(
            "candidate_profile_id", "reminder_type", name="uq_reminder_log_profile_type"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reminder_type: Mapped[ReminderType] = mapped_column(String(30), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<ReminderLog candidate_profile_id={self.candidate_profile_id} "
            f"reminder_type={self.reminder_type}>"
        )
