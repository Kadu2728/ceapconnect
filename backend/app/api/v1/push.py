"""Router de Push Notifications (EPIC 18 — PWA + push).

Rotas protegidas via `Depends(get_current_user)`. A regra de negócio vive em
`app.services.push_service` — o router apenas orquestra e envelopa.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.push import PushPublicKeyResponse, PushSubscribeRequest, PushUnsubscribeRequest
from app.schemas.response import ApiResponse
from app.services import push_service

router = APIRouter(prefix="/push", tags=["Push"])


@router.get(
    "/public-key",
    response_model=ApiResponse[PushPublicKeyResponse],
    summary="Chave pública VAPID para inscrição no push",
)
async def get_public_key() -> ApiResponse[PushPublicKeyResponse]:
    """Retorna a chave pública VAPID e se o push está disponível no servidor."""
    data = PushPublicKeyResponse(
        public_key=push_service.get_public_key(), configured=push_service.is_configured()
    )
    return ApiResponse(success=True, message="Chave pública recuperada.", data=data)


@router.post(
    "/subscribe",
    response_model=ApiResponse[None],
    summary="Inscreve o dispositivo atual para receber push",
)
async def subscribe(
    payload: PushSubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Registra a inscrição de push do navegador/dispositivo atual."""
    await push_service.subscribe(
        db, current_user, endpoint=payload.endpoint, p256dh=payload.p256dh, auth=payload.auth
    )
    return ApiResponse(success=True, message="Inscrição de push registrada.", data=None)


@router.post(
    "/unsubscribe",
    response_model=ApiResponse[None],
    summary="Cancela o push do dispositivo atual",
)
async def unsubscribe(
    payload: PushUnsubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Remove a inscrição de push do navegador/dispositivo atual."""
    await push_service.unsubscribe(db, current_user, endpoint=payload.endpoint)
    return ApiResponse(success=True, message="Inscrição de push removida.", data=None)
