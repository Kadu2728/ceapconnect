"""Router de Missões (EPIC 05).

Rotas protegidas via `Depends(get_current_user)`. Toda a regra de negócio
(listagem, conclusão, XP, desbloqueio de conquistas) vive em
`app.services.mission_service` — o router apenas orquestra e envelopa.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.mission import CompleteMissionResponse, MissionListResponse
from app.schemas.response import ApiResponse
from app.services import mission_service

router = APIRouter(prefix="/missions", tags=["Missões"])


@router.get(
    "",
    response_model=ApiResponse[MissionListResponse],
    summary="Lista as missões do candidato",
)
async def list_missions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MissionListResponse]:
    """Retorna todas as missões do candidato, com status e resumo de progresso."""
    data = await mission_service.list_missions(db, current_user)
    return ApiResponse(success=True, message="Missões recuperadas com sucesso.", data=data)


@router.post(
    "/{mission_id}/complete",
    response_model=ApiResponse[CompleteMissionResponse],
    summary="Conclui uma missão do candidato",
)
async def complete_mission(
    mission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CompleteMissionResponse]:
    """Conclui uma missão pendente: concede XP e desbloqueia conquistas elegíveis."""
    data = await mission_service.complete_mission(db, current_user, mission_id)
    return ApiResponse(success=True, message="Missão concluída com sucesso.", data=data)
