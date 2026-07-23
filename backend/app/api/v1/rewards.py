"""Router de Recompensas (EPIC 13).

Rotas protegidas via `Depends(get_current_user)`. Toda a regra de negócio
(listagem com status, avaliação de desbloqueio, resgate e notificação) vive em
`app.services.reward_service` — o router apenas orquestra e envelopa.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.reward import RedeemRewardResponse, RewardListResponse
from app.services import reward_service

router = APIRouter(prefix="/rewards", tags=["Recompensas"])


@router.get(
    "",
    response_model=ApiResponse[RewardListResponse],
    summary="Lista as recompensas do candidato",
)
async def list_rewards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RewardListResponse]:
    """Retorna o catálogo de recompensas com o nível e o status de cada item."""
    data = await reward_service.list_rewards(db, current_user)
    return ApiResponse(success=True, message="Recompensas recuperadas com sucesso.", data=data)


@router.post(
    "/{reward_id}/redeem",
    response_model=ApiResponse[RedeemRewardResponse],
    summary="Resgata uma recompensa desbloqueada",
)
async def redeem_reward(
    reward_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RedeemRewardResponse]:
    """Resgata uma recompensa: gera o pedido de entrega e notifica o candidato."""
    data = await reward_service.redeem_reward(db, current_user, reward_id)
    return ApiResponse(success=True, message="Recompensa resgatada com sucesso.", data=data)
