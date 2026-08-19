"""add candidate status, risk score history and model version

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-08-19 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). Fase 2 da
evolução do sistema de predição de evasão (moat): registra o outcome real do
candidato (`status`) para servir de rótulo no backtest do modelo de risco,
grava o histórico de scores em `risk_score_history` (append-only —
`risk_scores` continua upsert-only, guardando só o estado atual) e versiona
qual implementação de `RiskScorer` gerou cada score (`model_version`).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: str | None = "e1f2a3b4c5d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "candidate_profiles",
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
    )
    op.add_column(
        "candidate_profiles",
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_check_constraint(
        "ck_candidate_profile_status",
        "candidate_profiles",
        "status IN ('active', 'approved', 'evaded', 'withdrawn')",
    )

    op.add_column(
        "risk_scores",
        sa.Column(
            "model_version",
            sa.String(length=50),
            server_default="heuristic-v1",
            nullable=False,
        ),
    )

    op.create_table(
        "risk_score_history",
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
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_risk_score_history_candidate_computed",
        "risk_score_history",
        ["candidate_profile_id", "computed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_risk_score_history_candidate_computed", table_name="risk_score_history")
    op.drop_table("risk_score_history")

    op.drop_column("risk_scores", "model_version")

    op.drop_constraint("ck_candidate_profile_status", "candidate_profiles", type_="check")
    op.drop_column("candidate_profiles", "status_changed_at")
    op.drop_column("candidate_profiles", "status")
