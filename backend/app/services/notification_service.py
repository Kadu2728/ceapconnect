"""Regra de negócio da Central de Notificações (EPIC 08).

Lista as notificações do candidato e permite marcá-las como lidas (uma a uma ou
todas de uma vez). Notificações são criadas por outras features (eventos,
recompensas, sistema) — aqui só há leitura e atualização do status `read`.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    MarkAllReadResponse,
    NotificationItem,
    NotificationListResponse,
)
from app.services.candidate_profile_service import get_profile_or_raise


async def list_notifications(db: AsyncSession, user: User) -> NotificationListResponse:
    """Retorna as notificações do candidato com a contagem de não lidas."""
    profile = await get_profile_or_raise(db, user)
    repo = NotificationRepository(db)

    rows = await repo.list_for_profile(profile.id)
    unread_count = await repo.count_unread_for_profile(profile.id)

    return NotificationListResponse(
        notifications=[
            NotificationItem(
                id=row.id,
                title=row.title,
                description=row.description,
                category=row.category,
                read=row.read,
                created_at=row.created_at,
            )
            for row in rows
        ],
        unread_count=unread_count,
    )


async def mark_read(db: AsyncSession, user: User, notification_id: uuid.UUID) -> NotificationItem:
    """Marca uma notificação do candidato como lida (404 se não for dele)."""
    profile = await get_profile_or_raise(db, user)
    repo = NotificationRepository(db)

    notification = await repo.get_for_profile(
        candidate_profile_id=profile.id, notification_id=notification_id
    )
    if notification is None:
        raise NotFoundException("Notificação não encontrada.")

    if not notification.read:
        await repo.mark_read(notification)
        await db.commit()

    return NotificationItem(
        id=notification.id,
        title=notification.title,
        description=notification.description,
        category=notification.category,
        read=notification.read,
        created_at=notification.created_at,
    )


async def mark_all_read(db: AsyncSession, user: User) -> MarkAllReadResponse:
    """Marca todas as notificações não lidas do candidato como lidas."""
    profile = await get_profile_or_raise(db, user)
    repo = NotificationRepository(db)

    marked = await repo.mark_all_read_for_profile(profile.id)
    await db.commit()

    unread_count = await repo.count_unread_for_profile(profile.id)
    return MarkAllReadResponse(marked=marked, unread_count=unread_count)
