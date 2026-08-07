"""create risk_scores and interventions

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-08-08 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). Fase 3 da
EPIC 14 (Predição de evasão). Espelha:
- `app.models.risk_score.RiskScore` (estado atual de risco por candidato);
- `app.models.intervention.Intervention` (contatos registrados + medição de
  impacto 7 dias depois).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: str | None = "f6a7b8c9d0e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "risk_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("tier", sa.String(length=10), nullable=False),
        sa.Column(
            "factors",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("explanation", sa.String(length=500), nullable=False),
        sa.Column(
            "features",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "tier IN ('baixo', 'medio', 'alto')",
            name="ck_risk_score_tier",
        ),
        sa.UniqueConstraint("candidate_profile_id", name="uq_risk_score_candidate_profile"),
    )
    op.create_index(
        op.f("ix_risk_scores_candidate_profile_id"), "risk_scores", ["candidate_profile_id"]
    )
    op.create_index(op.f("ix_risk_scores_tier"), "risk_scores", ["tier"])

    op.create_table(
        "interventions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
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
        sa.Column("score_at_creation", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score_after", sa.Integer(), nullable=True),
        sa.Column("had_activity_after", sa.Boolean(), nullable=True),
        sa.CheckConstraint(
            "channel IN ('call', 'whatsapp', 'other')",
            name="ck_intervention_channel",
        ),
        sa.CheckConstraint(
            "outcome IN ('reached', 'no_answer', 'other')",
            name="ck_intervention_outcome",
        ),
    )
    op.create_index(
        op.f("ix_interventions_candidate_profile_id"), "interventions", ["candidate_profile_id"]
    )
    op.create_index(op.f("ix_interventions_created_at"), "interventions", ["created_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_interventions_created_at"), table_name="interventions")
    op.drop_index(op.f("ix_interventions_candidate_profile_id"), table_name="interventions")
    op.drop_table("interventions")

    op.drop_index(op.f("ix_risk_scores_tier"), table_name="risk_scores")
    op.drop_index(op.f("ix_risk_scores_candidate_profile_id"), table_name="risk_scores")
    op.drop_table("risk_scores")
