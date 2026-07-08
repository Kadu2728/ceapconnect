"""Router de Conquistas (EPIC 06).

Rota protegida via `Depends(get_current_user)`. A regra de negócio vive em
`app.services.achievement_service`.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.achievement import AchievementListResponse
from app.schemas.response import ApiResponse
from app.services import achievement_service

router = APIRouter(prefix="/achievements", tags=["Conquistas"])


@router.get(
    "",
    response_model=ApiResponse[AchievementListResponse],
    summary="Lista as conquistas do candidato",
)
async def list_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AchievementListResponse]:
    """Retorna o catálogo de conquistas com o status de desbloqueio do candidato."""
    data = await achievement_service.list_achievements(db, current_user)
    return ApiResponse(success=True, message="Conquistas recuperadas com sucesso.", data=data)
