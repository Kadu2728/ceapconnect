"""create users table

Revision ID: a1a97ff6f1fa
Revises:
Create Date: 2026-07-02 00:00:00.000000

Migration escrita manualmente (sem `alembic revision --autogenerate`), pois
ainda não há uma connection string real de Postgres disponível no ambiente
de desenvolvimento (aguardando provisionamento do Neon). O schema abaixo
espelha 100% o model `app.models.user.User` — conferir os dois em conjunto
caso este arquivo precise ser alterado no futuro.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1a97ff6f1fa"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("cpf", sa.String(length=11), nullable=False),
        sa.Column("phone", sa.String(length=11), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_cpf"), "users", ["cpf"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_cpf"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
