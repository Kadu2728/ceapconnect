"""add guardians.activated_by_user_id (RBAC do responsável — fase B)

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-08-29 00:00:00.000000

Fase B do RBAC do responsável: ativação de conta a partir do link mágico.

`guardians.activated_by_user_id` marca que aquele registro de contato já foi
usado para criar uma conta de login (`users.role == 'guardian'`) — torna a
ativação idempotente (mesmo link clicado duas vezes não cria uma segunda
conta) e permite o portal público mostrar "faça login" depois da primeira
ativação. Aditivo, nullable, sem impacto em nenhuma rota existente.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "f4a5b6c7d8e9"
down_revision: str | None = "e3f4a5b6c7d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "guardians",
        sa.Column(
            "activated_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("guardians", "activated_by_user_id")
