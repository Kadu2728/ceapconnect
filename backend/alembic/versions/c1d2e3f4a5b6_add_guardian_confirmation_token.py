"""add guardian confirmation_token + training_notice_sent_at

Revision ID: c1d2e3f4a5b6
Revises: e0a6a83000f1
Create Date: 2026-08-25 00:00:00.000000

Item 5 do backlog — "confirmação de presença pelo próprio responsável".
`confirmation_token` é adicionado nullable, retroativamente preenchido com
um token único por linha já existente (nenhum responsável cadastrado antes
desta migration fica sem link mágico), depois promovido a NOT NULL + UNIQUE.
"""

import secrets
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: str | None = "b9c0d1e2f3a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("guardians", sa.Column("confirmation_token", sa.String(length=64), nullable=True))
    op.add_column(
        "guardians",
        sa.Column("training_notice_sent_at", sa.DateTime(timezone=True), nullable=True),
    )

    guardians = sa.table(
        "guardians",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("confirmation_token", sa.String),
    )
    conn = op.get_bind()
    existing_ids = [row[0] for row in conn.execute(sa.select(guardians.c.id))]
    for guardian_id in existing_ids:
        conn.execute(
            guardians.update()
            .where(guardians.c.id == guardian_id)
            .values(confirmation_token=secrets.token_urlsafe(32))
        )

    op.alter_column("guardians", "confirmation_token", nullable=False)
    op.create_unique_constraint(
        "uq_guardian_confirmation_token", "guardians", ["confirmation_token"]
    )
    op.create_index("ix_guardians_confirmation_token", "guardians", ["confirmation_token"])


def downgrade() -> None:
    op.drop_index("ix_guardians_confirmation_token", table_name="guardians")
    op.drop_constraint("uq_guardian_confirmation_token", "guardians", type_="unique")
    op.drop_column("guardians", "confirmation_token")
    op.drop_column("guardians", "training_notice_sent_at")
