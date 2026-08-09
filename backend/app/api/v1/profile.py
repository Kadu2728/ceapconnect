"""Router da Tela de Perfil (EPIC 09).

Rotas protegidas via `Depends(get_current_user)`. A regra de negócio vive em
`app.services.profile_service` — o router apenas orquestra e envelopa.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.profile import GuardianEmailNoticeResult, ProfileResponse, ProfileUpdateRequest
from app.schemas.response import ApiResponse
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["Perfil"])


@router.get(
    "",
    response_model=ApiResponse[ProfileResponse],
    summary="Perfil do candidato (dados + gamificação)",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ProfileResponse]:
    """Retorna os dados cadastrais e o resumo de gamificação do candidato."""
    data = await profile_service.get_profile(db, current_user)
    return ApiResponse(success=True, message="Perfil recuperado com sucesso.", data=data)


@router.patch(
    "",
    response_model=ApiResponse[ProfileResponse],
    summary="Atualiza o perfil do candidato",
)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ProfileResponse]:
    """Atualiza nome/telefone e desbloqueia a conquista de perfil completo."""
    data = await profile_service.update_profile(db, current_user, payload)
    return ApiResponse(success=True, message="Perfil atualizado com sucesso.", data=data)


@router.post(
    "/guardian/notify-email",
    response_model=ApiResponse[GuardianEmailNoticeResult],
    summary="Avisa o responsável por e-mail sobre a entrevista",
)
async def notify_guardian_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianEmailNoticeResult]:
    """Envia o e-mail de aviso da entrevista ao responsável (EPIC 17)."""
    data = await profile_service.notify_guardian_email(db, current_user)
    return ApiResponse(success=True, message=data.message, data=data)
