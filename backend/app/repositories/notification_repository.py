"""Acesso a dados da entidade `Notification` (EPIC 03/08 — Notificações).

Isola toda query relacionada a notificações — a camada de services nunca
deve montar SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationCategory


class NotificationRepository:
    """Repositório de leitura/escrita de notificações por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        title: str,
        description: str,
        category: NotificationCategory,
    ) -> Notification:
        """Cria uma notificação para o candidato (flush, sem commit)."""
        notification = Notification(
            candidate_profile_id=candidate_profile_id,
            title=title,
            description=description,
            category=category,
        )
        self._db.add(notification)
        await self._db.flush()
        return notification

    async def count_unread_for_profile(self, candidate_profile_id: uuid.UUID) -> int:
        """Conta as notificações não lidas do candidato."""
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.candidate_profile_id == candidate_profile_id,
                Notification.read.is_(False),
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar_one()
