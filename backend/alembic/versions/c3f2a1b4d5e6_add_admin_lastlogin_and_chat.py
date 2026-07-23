"""add is_admin + last_login_at to users and create chat_messages

Revision ID: c3f2a1b4d5e6
Revises: 8d32aeff4fe7
Create Date: 2026-07-07 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). Espelha:
- `app.models.user.User` (novas colunas `is_admin`, `last_login_at`);
- `app.models.chat_message.ChatMessage` (nova tabela do assistente de IA).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "c3f2a1b4d5e6"
down_revision: str | None = "8d32aeff4fe7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="ck_chat_message_role"),
    )
    op.create_index(
        op.f("ix_chat_messages_candidate_profile_id"),
        "chat_messages",
        ["candidate_profile_id"],
    )
    op.create_index(
        op.f("ix_chat_messages_created_at"),
        "chat_messages",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_chat_messages_created_at"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_candidate_profile_id"), table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "is_admin")
