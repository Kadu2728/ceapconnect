"""Router de Eventos (EPIC 07).

Rotas protegidas via `Depends(get_current_user)`. A regra de negócio vive em
`app.services.event_service`.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.event import EventListResponse, EventRegistrationResponse
from app.schemas.response import ApiResponse
from app.services import event_service

router = APIRouter(prefix="/events", tags=["Eventos"])


@router.get(
    "",
    response_model=ApiResponse[EventListResponse],
    summary="Lista os próximos eventos",
)
async def list_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[EventListResponse]:
    """Retorna os próximos eventos com o status de inscrição do candidato."""
    data = await event_service.list_events(db, current_user)
    return ApiResponse(success=True, message="Eventos recuperados com sucesso.", data=data)


@router.post(
    "/{event_id}/register",
    response_model=ApiResponse[EventRegistrationResponse],
    summary="Inscreve o candidato em um evento",
)
async def register_event(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[EventRegistrationResponse]:
    """Inscreve o candidato no evento e envia a notificação de confirmação."""
    data = await event_service.register_event(db, current_user, event_id)
    return ApiResponse(success=True, message="Inscrição realizada com sucesso.", data=data)


@router.delete(
    "/{event_id}/register",
    response_model=ApiResponse[EventRegistrationResponse],
    summary="Cancela a inscrição do candidato em um evento",
)
async def cancel_registration(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[EventRegistrationResponse]:
    """Cancela a inscrição do candidato no evento."""
    data = await event_service.cancel_registration(db, current_user, event_id)
    return ApiResponse(success=True, message="Inscrição cancelada com sucesso.", data=data)
