"""Regra de negócio da Central de Notificações (EPIC 08).

Lista as notificações do candidato, permite marcá-las como lidas (uma a uma ou
todas de uma vez), e centraliza a criação de notificações por outras features
(eventos, recompensas, sistema) via `create_notification` — ponto único que
também dispara o push (EPIC 18), para nenhuma feature esquecer de avisar o
candidato nos dois canais.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.notification import Notification, NotificationCategory
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    MarkAllReadResponse,
    NotificationItem,
    NotificationListResponse,
)
from app.services import push_service
from app.services.candidate_profile_service import get_profile_or_raise


async def create_notification(
    db: AsyncSession,
    *,
    candidate_profile_id: uuid.UUID,
    title: str,
    description: str,
    category: NotificationCategory,
) -> Notification:
    """Cria a notificação in-app e dispara o push (best-effort) do mesmo
    conteúdo. Não commita — participa da transação do chamador, como antes.
    """
    notification = await NotificationRepository(db).create(
        candidate_profile_id=candidate_profile_id,
        title=title,
        description=description,
        category=category,
    )
    await push_service.send_push_to_profile(db, candidate_profile_id, title=title, body=description)
    return notification


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
