"""Router do onboarding do primeiro login (EPIC 12 — UX)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.response import ApiResponse
from app.services import onboarding_service

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post(
    "/complete",
    response_model=ApiResponse[None],
    summary="Marca o onboarding (boas-vindas) como concluído",
)
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Registra que o candidato já viu a tela de boas-vindas."""
    await onboarding_service.complete(db, current_user)
    return ApiResponse(success=True, message="Onboarding concluído.", data=None)
