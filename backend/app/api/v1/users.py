"""Router de perfil do usuário autenticado (EPIC 02).

Rota protegida via `Depends(get_current_user)` — nunca faz verificação
manual de token.
"""

from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.user import UserMe
from app.services.user_service import get_current_user_profile

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse[UserMe], summary="Perfil do usuário autenticado")
async def get_me(current_user: User = Depends(get_current_user)) -> ApiResponse[UserMe]:
    """Retorna o perfil completo do usuário autenticado (sem dados sensíveis)."""
    data = get_current_user_profile(current_user)
    return ApiResponse(success=True, message="Perfil recuperado com sucesso.", data=data)
