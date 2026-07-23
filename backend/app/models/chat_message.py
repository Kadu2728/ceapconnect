"""Model SQLAlchemy da entidade `ChatMessage` (EPIC 11 — Assistente IA).

Histórico da conversa de cada candidato com o assistente (bot). Cada linha é
uma mensagem imutável (`user` ou `assistant`), preservando o contexto para as
próximas respostas do modelo e para o candidato reabrir o chat.

`role` é modelado como `String` + `CHECK CONSTRAINT` (mesmo racional de
`MissionProgress`): o conjunto de papéis é pequeno e estável, mas pode evoluir
(ex.: "system") sem o custo de um `ALTER TYPE` de ENUM nativo.
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

ChatRole = Literal["user", "assistant"]

ROLE_USER: Final = "user"
ROLE_ASSISTANT: Final = "assistant"
_VALID_ROLES: Final = (ROLE_USER, ROLE_ASSISTANT)


class ChatMessage(Base):
    """Uma mensagem da conversa entre um candidato e o assistente de IA."""

    __tablename__ = "chat_messages"
    __table_args__ = (CheckConstraint(f"role IN {_VALID_ROLES}", name="ck_chat_message_role"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[ChatRole] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ChatMessage candidate_profile_id={self.candidate_profile_id} role={self.role}>"
