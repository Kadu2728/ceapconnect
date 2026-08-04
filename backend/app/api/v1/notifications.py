"""Router da Central de Notificações (EPIC 08).

Rotas protegidas via `Depends(get_current_user)`. A regra de negócio vive em
`app.services.notification_service` — o router apenas orquestra e envelopa.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import (
    MarkAllReadResponse,
    NotificationItem,
    NotificationListResponse,
)
from app.schemas.response import ApiResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notificações"])


@router.get(
    "",
    response_model=ApiResponse[NotificationListResponse],
    summary="Lista as notificações do candidato",
)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NotificationListResponse]:
    """Retorna as notificações do candidato, mais recentes primeiro."""
    data = await notification_service.list_notifications(db, current_user)
    return ApiResponse(success=True, message="Notificações recuperadas com sucesso.", data=data)


@router.post(
    "/read-all",
    response_model=ApiResponse[MarkAllReadResponse],
    summary="Marca todas as notificações como lidas",
)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MarkAllReadResponse]:
    """Marca todas as notificações não lidas do candidato como lidas."""
    data = await notification_service.mark_all_read(db, current_user)
    return ApiResponse(success=True, message="Notificações marcadas como lidas.", data=data)


@router.post(
    "/{notification_id}/read",
    response_model=ApiResponse[NotificationItem],
    summary="Marca uma notificação como lida",
)
async def mark_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NotificationItem]:
    """Marca uma notificação específica do candidato como lida."""
    data = await notification_service.mark_read(db, current_user, notification_id)
    return ApiResponse(success=True, message="Notificação marcada como lida.", data=data)
