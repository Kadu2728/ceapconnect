"""Router do Portal do Responsável (link mágico, sem conta/login).

Deliberadamente público — nem `Depends(get_current_user)` nem `CohortScope`.
A posse do `token` (32 bytes aleatórios, ver `app.models.guardian.
_generate_confirmation_token`) é a única autorização, mesmo racional de um
link de reset de senha. Nunca expõe dado além do necessário para a tela de
confirmação (ver `GuardianPortalView`).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import TokenPairResponse
from app.schemas.guardian_portal import GuardianAccountActivationRequest, GuardianPortalView
from app.schemas.response import ApiResponse
from app.services import guardian_portal_service

router = APIRouter(prefix="/guardian-portal", tags=["Portal do Responsável"])


@router.get(
    "/{token}",
    response_model=ApiResponse[GuardianPortalView],
    summary="Dados exibidos ao responsável na tela de confirmação",
)
async def get_guardian_portal(
    token: str, db: AsyncSession = Depends(get_db)
) -> ApiResponse[GuardianPortalView]:
    data = await guardian_portal_service.get_portal_view(db, token)
    return ApiResponse(success=True, message="Dados recuperados com sucesso.", data=data)


@router.post(
    "/{token}/confirm",
    response_model=ApiResponse[GuardianPortalView],
    summary="Responsável confirma presença na formação obrigatória",
)
async def confirm_guardian_training(
    token: str, db: AsyncSession = Depends(get_db)
) -> ApiResponse[GuardianPortalView]:
    data = await guardian_portal_service.confirm_training(db, token)
    return ApiResponse(success=True, message="Presença confirmada com sucesso.", data=data)


@router.post(
    "/{token}/activate",
    response_model=ApiResponse[TokenPairResponse],
    summary="Responsável cria sua conta de login a partir do link mágico",
)
async def activate_guardian_account(
    token: str,
    payload: GuardianAccountActivationRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenPairResponse]:
    data = await guardian_portal_service.activate_account(db, token, payload)
    return ApiResponse(success=True, message="Conta criada com sucesso.", data=data)
