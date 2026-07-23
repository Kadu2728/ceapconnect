"""Acesso a dados da entidade `ChatMessage` (EPIC 11 — Assistente IA).

Isola toda query relacionada ao histórico de conversa do candidato com o
assistente — a camada de services nunca deve montar SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage, ChatRole


class ChatMessageRepository:
    """Repositório de leitura/escrita do histórico de chat por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_for_profile(
        self, candidate_profile_id: uuid.UUID, *, limit: int = 50
    ) -> list[ChatMessage]:
        """Retorna as últimas mensagens do candidato, em ordem cronológica.

        Aplica um `limit` para não crescer o contexto (e o custo) sem limite —
        pega as `limit` mais recentes e as devolve na ordem correta (antiga →
        recente) para reconstruir a conversa.
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.candidate_profile_id == candidate_profile_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        rows = list((await self._db.execute(stmt)).scalars().all())
        rows.reverse()
        return rows

    async def create(
        self, *, candidate_profile_id: uuid.UUID, role: ChatRole, content: str
    ) -> ChatMessage:
        """Persiste uma mensagem do chat (flush, sem commit)."""
        message = ChatMessage(
            candidate_profile_id=candidate_profile_id,
            role=role,
            content=content,
        )
        self._db.add(message)
        await self._db.flush()
        return message
