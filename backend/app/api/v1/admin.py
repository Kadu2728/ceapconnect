"""Router do painel administrativo (EPIC 10).

Todas as rotas são protegidas por `Depends(get_current_admin)` — 403 para
usuários autenticados sem `is_admin`. A regra de negócio vive em
`app.services.admin_service`.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.admin import (
    AdminOverview,
    AdminRedemptionItem,
    AdminRedemptionListResponse,
)
from app.schemas.admin_reward import (
    AdminRewardItem,
    AdminRewardListResponse,
    AdminRewardWrite,
)
from app.schemas.response import ApiResponse
from app.services import admin_reward_service, admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/overview",
    response_model=ApiResponse[AdminOverview],
    summary="Métricas gerais da plataforma",
)
async def get_overview(
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminOverview]:
    """Retorna as métricas de acesso e engajamento dos alunos."""
    data = await admin_service.get_overview(db)
    return ApiResponse(success=True, message="Métricas recuperadas com sucesso.", data=data)


@router.get(
    "/redemptions",
    response_model=ApiResponse[AdminRedemptionListResponse],
    summary="Fila de resgates de recompensas",
)
async def list_redemptions(
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminRedemptionListResponse]:
    """Lista os resgates de recompensas dos alunos (fila de entrega)."""
    data = await admin_service.list_redemptions(db)
    return ApiResponse(success=True, message="Resgates recuperados com sucesso.", data=data)


@router.post(
    "/redemptions/{redemption_id}/fulfill",
    response_model=ApiResponse[AdminRedemptionItem],
    summary="Confirma a entrega de um resgate",
)
async def fulfill_redemption(
    redemption_id: uuid.UUID,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminRedemptionItem]:
    """Marca um resgate como entregue e notifica o aluno."""
    data = await admin_service.fulfill_redemption(db, redemption_id)
    return ApiResponse(success=True, message="Entrega confirmada com sucesso.", data=data)


@router.get(
    "/rewards",
    response_model=ApiResponse[AdminRewardListResponse],
    summary="Gestão do catálogo de recompensas",
)
async def list_rewards(
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminRewardListResponse]:
    """Lista todas as recompensas (ativas e inativas) + conquistas para o seletor."""
    data = await admin_reward_service.list_rewards(db)
    return ApiResponse(success=True, message="Recompensas recuperadas com sucesso.", data=data)


@router.post(
    "/rewards",
    response_model=ApiResponse[AdminRewardItem],
    status_code=201,
    summary="Cria uma recompensa",
)
async def create_reward(
    payload: AdminRewardWrite,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminRewardItem]:
    """Cria uma nova recompensa no catálogo."""
    data = await admin_reward_service.create_reward(db, payload)
    return ApiResponse(success=True, message="Recompensa criada com sucesso.", data=data)


@router.patch(
    "/rewards/{reward_id}",
    response_model=ApiResponse[AdminRewardItem],
    summary="Atualiza uma recompensa",
)
async def update_reward(
    reward_id: uuid.UUID,
    payload: AdminRewardWrite,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminRewardItem]:
    """Atualiza uma recompensa existente (dados, condição, destaque, ativação)."""
    data = await admin_reward_service.update_reward(db, reward_id, payload)
    return ApiResponse(success=True, message="Recompensa atualizada com sucesso.", data=data)
