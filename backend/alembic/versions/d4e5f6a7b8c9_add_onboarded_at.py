"""add onboarded_at to candidate_profiles

Revision ID: d4e5f6a7b8c9
Revises: c3f2a1b4d5e6
Create Date: 2026-07-07 00:00:00.000000

Migration manual (mesmo padrão das anteriores). Espelha o novo campo
`onboarded_at` de `app.models.candidate_profile.CandidateProfile` — usado pela
tela de boas-vindas do primeiro login (EPIC 12 — UX).
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c3f2a1b4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "candidate_profiles",
        sa.Column("onboarded_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("candidate_profiles", "onboarded_at")
