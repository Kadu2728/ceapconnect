"""add guardian and interview fields

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-08-09 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). EPIC 17
(Envolver o responsável). Espelha os novos campos de
`app.models.candidate_profile.CandidateProfile`.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: str | None = "c9d0e1f2a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("candidate_profiles", sa.Column("interview_date", sa.Date(), nullable=True))
    op.add_column(
        "candidate_profiles", sa.Column("guardian_name", sa.String(length=150), nullable=True)
    )
    op.add_column(
        "candidate_profiles", sa.Column("guardian_phone", sa.String(length=11), nullable=True)
    )
    op.add_column(
        "candidate_profiles", sa.Column("guardian_email", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "candidate_profiles",
        sa.Column("guardian_notified_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("candidate_profiles", "guardian_notified_at")
    op.drop_column("candidate_profiles", "guardian_email")
    op.drop_column("candidate_profiles", "guardian_phone")
    op.drop_column("candidate_profiles", "guardian_name")
    op.drop_column("candidate_profiles", "interview_date")
