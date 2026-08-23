"""create guardian_interventions and the guardian-training achievement

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-08-20 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). Fecha o alvo
duplo do Console de Intervenção (também responsáveis, não só candidatos) e o
marco visual "Responsável na Jornada" (conquista simbólica, sem XP — ver
`app.services.achievement_service.unlock_guardian_training`).

A conquista é inserida aqui (não só no `app/core/seed.py`) porque o seed é um
script manual (`python -m app.core.seed`), nunca rodado automaticamente no
boot — só a migration roda garantidamente em todo deploy.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "d6e7f8a9b0c1"
down_revision: str | None = "c5d6e7f8a9b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ACHIEVEMENT_NAME = "Responsável na Jornada"


def upgrade() -> None:
    op.create_table(
        "guardian_interventions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "guardian_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("guardians.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "channel IN ('call', 'whatsapp', 'other')",
            name="ck_guardian_intervention_channel",
        ),
        sa.CheckConstraint(
            "outcome IN ('reached', 'no_answer', 'other')",
            name="ck_guardian_intervention_outcome",
        ),
    )
    op.create_index(
        op.f("ix_guardian_interventions_guardian_id"), "guardian_interventions", ["guardian_id"]
    )
    op.create_index(
        op.f("ix_guardian_interventions_created_at"), "guardian_interventions", ["created_at"]
    )

    op.execute(f"""
        INSERT INTO achievements (id, name, description, icon, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            '{_ACHIEVEMENT_NAME}',
            'Seu responsável concluiu a formação obrigatória do processo seletivo.',
            'heart-handshake',
            now(),
            now()
        WHERE NOT EXISTS (SELECT 1 FROM achievements WHERE name = '{_ACHIEVEMENT_NAME}')
    """)


def downgrade() -> None:
    op.execute(f"DELETE FROM achievements WHERE name = '{_ACHIEVEMENT_NAME}'")

    op.drop_index(op.f("ix_guardian_interventions_created_at"), table_name="guardian_interventions")
    op.drop_index(
        op.f("ix_guardian_interventions_guardian_id"), table_name="guardian_interventions"
    )
    op.drop_table("guardian_interventions")
