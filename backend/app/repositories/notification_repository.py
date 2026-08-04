"""Acesso a dados da entidade `Notification` (EPIC 03/08 — Notificações).

Isola toda query relacionada a notificações — a camada de services nunca
deve montar SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import func, select, update
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

    async def list_for_profile(
        self, candidate_profile_id: uuid.UUID, *, limit: int = 50
    ) -> list[Notification]:
        """Notificações do candidato, mais recentes primeiro."""
        stmt = (
            select(Notification)
            .where(Notification.candidate_profile_id == candidate_profile_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def get_for_profile(
        self, *, candidate_profile_id: uuid.UUID, notification_id: uuid.UUID
    ) -> Notification | None:
        """Uma notificação específica do candidato (garante a posse)."""
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.candidate_profile_id == candidate_profile_id,
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def mark_read(self, notification: Notification) -> None:
        """Marca uma notificação como lida (flush, sem commit)."""
        notification.read = True
        await self._db.flush()

    async def mark_all_read_for_profile(self, candidate_profile_id: uuid.UUID) -> int:
        """Marca todas as não lidas do candidato como lidas. Retorna quantas mudaram."""
        stmt = (
            update(Notification)
            .where(
                Notification.candidate_profile_id == candidate_profile_id,
                Notification.read.is_(False),
            )
            .values(read=True)
        )
        result = await self._db.execute(stmt)
        return result.rowcount or 0
