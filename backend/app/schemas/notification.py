"""Schemas Pydantic da Central de Notificações (EPIC 08).

Contrato de:
- `GET  /api/v1/notifications`            → lista + contagem de não lidas;
- `POST /api/v1/notifications/{id}/read`  → marca uma como lida;
- `POST /api/v1/notifications/read-all`   → marca todas como lidas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.notification import NotificationCategory


class NotificationItem(BaseModel):
    """Uma notificação do candidato."""

    id: uuid.UUID
    title: str
    description: str
    category: NotificationCategory
    read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Payload de `GET /api/v1/notifications`."""

    notifications: list[NotificationItem]
    unread_count: int


class MarkAllReadResponse(BaseModel):
    """Payload de `POST /api/v1/notifications/read-all`."""

    marked: int
    unread_count: int
