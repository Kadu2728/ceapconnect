"""add journey_pauses + eventos de pausa (Jornada que Respira — fase 1)

Revision ID: a5b6c7d8e9f0
Revises: f4a5b6c7d8e9
Create Date: 2026-08-30 00:00:00.000000

Pausa Declarada: o candidato avisa que a vida apertou, em vez de sumir.

- `journey_pauses`: uma linha por pausa (histórico, não estado atual — a
  métrica "de quem pausou, quantos retomaram" exige todas as pausas).
- `activity_events.name` ganha `pause_started`/`pause_resumed`/
  `pause_expired` (extensão do CHECK existente, sem renomear nada).

Aditivo: nenhuma rota ou tabela existente muda de comportamento.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a5b6c7d8e9f0"
down_revision: str | None = "f4a5b6c7d8e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_OLD_EVENT_NAMES = (
    "login",
    "step_viewed",
    "step_completed",
    "step_abandoned",
    "step_resumed",
    "mission_started",
    "mission_completed",
    "mission_abandoned",
    "document_uploaded",
    "nba_generated",
    "nba_clicked",
    "nba_completed",
    "recovery_entered",
    "recovery_completed",
    "recovery_exited",
)
_NEW_EVENT_NAMES = (*_OLD_EVENT_NAMES, "pause_started", "pause_resumed", "pause_expired")

_PAUSE_STATUSES = ("active", "resumed", "expired")
_REASON_CODES = ("trabalho", "tempo", "outro")


def upgrade() -> None:
    op.create_table(
        "journey_pauses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("requested_days", sa.SmallInteger(), nullable=False),
        sa.Column("reason_code", sa.String(length=20), nullable=True),
        sa.Column("paused_at_step_key", sa.String(length=50), nullable=True),
        sa.Column("resume_action_key", sa.String(length=30), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("status IN " + str(_PAUSE_STATUSES), name="ck_journey_pause_status"),
        sa.CheckConstraint(
            "reason_code IS NULL OR reason_code IN " + str(_REASON_CODES),
            name="ck_journey_pause_reason",
        ),
        sa.CheckConstraint("ends_at > started_at", name="ck_journey_pause_window"),
        sa.CheckConstraint(
            "(status = 'active') = (ended_at IS NULL)", name="ck_journey_pause_ended_at"
        ),
    )

    # Só uma pausa ativa por candidato — invariante no banco, não em código.
    op.create_index(
        "uq_journey_pause_one_active",
        "journey_pauses",
        ["candidate_profile_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "ix_journey_pauses_candidate",
        "journey_pauses",
        ["candidate_profile_id", "started_at"],
    )
    op.create_index(
        "ix_journey_pauses_due",
        "journey_pauses",
        ["ends_at"],
        postgresql_where=sa.text("status = 'active'"),
    )

    op.drop_constraint("ck_activity_event_name", "activity_events", type_="check")
    op.create_check_constraint(
        "ck_activity_event_name", "activity_events", "name IN " + str(_NEW_EVENT_NAMES)
    )


def downgrade() -> None:
    op.drop_constraint("ck_activity_event_name", "activity_events", type_="check")
    op.create_check_constraint(
        "ck_activity_event_name", "activity_events", "name IN " + str(_OLD_EVENT_NAMES)
    )

    op.drop_index("ix_journey_pauses_due", table_name="journey_pauses")
    op.drop_index("ix_journey_pauses_candidate", table_name="journey_pauses")
    op.drop_index("uq_journey_pause_one_active", table_name="journey_pauses")
    op.drop_table("journey_pauses")
