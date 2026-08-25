"""create reminder_logs (lembretes automáticos)

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
Create Date: 2026-08-25 00:00:00.000000

Migração aditiva. Espelha `app.models.reminder_log.ReminderLog`: um
registro por (candidato, tipo de lembrete) já enviado, para o job de
lembretes (`app.services.reminder_service`) nunca reenviar o mesmo aviso.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b9c0d1e2f3a4"
down_revision: str | None = "a8b9c0d1e2f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_REMINDER_TYPES = (
    "exam_7_days",
    "exam_1_day",
    "interview_7_days",
    "interview_1_day",
    "documentation_incomplete",
)


def upgrade() -> None:
    op.create_table(
        "reminder_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reminder_type", sa.String(length=30), nullable=False),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "reminder_type IN " + str(_REMINDER_TYPES),
            name="ck_reminder_log_type",
        ),
        sa.UniqueConstraint(
            "candidate_profile_id", "reminder_type", name="uq_reminder_log_profile_type"
        ),
    )
    op.create_index(
        "ix_reminder_logs_candidate_profile_id", "reminder_logs", ["candidate_profile_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_reminder_logs_candidate_profile_id", table_name="reminder_logs")
    op.drop_table("reminder_logs")
