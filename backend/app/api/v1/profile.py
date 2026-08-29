"""Router da Tela de Perfil (EPIC 09).

Rotas protegidas via `Depends(get_current_user)`. A regra de negócio vive em
`app.services.profile_service` — o router apenas orquestra e envelopa.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.guardian_consent import GuardianLinkConsentItem, GuardianLinkConsentListResponse
from app.schemas.profile import (
    GuardianEmailNoticeResult,
    GuardianTrainingEmailNoticeResult,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.schemas.response import ApiResponse
from app.services import guardian_consent_service, profile_service

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


@router.post(
    "/guardian/notify-training",
    response_model=ApiResponse[GuardianTrainingEmailNoticeResult],
    summary="Avisa o responsável por e-mail sobre a formação obrigatória",
)
async def notify_guardian_training(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianTrainingEmailNoticeResult]:
    """Envia o e-mail de aviso da formação obrigatória, com o link de
    confirmação de presença (item 5 do backlog)."""
    data = await profile_service.notify_guardian_training_email(db, current_user)
    return ApiResponse(success=True, message=data.message, data=data)


@router.get(
    "/guardian-links",
    response_model=ApiResponse[GuardianLinkConsentListResponse],
    summary="Responsáveis que pediram vínculo com sua conta (RBAC do responsável — fase C)",
)
async def list_guardian_links(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianLinkConsentListResponse]:
    data = await guardian_consent_service.list_links(db, current_user)
    return ApiResponse(success=True, message="Vínculos recuperados com sucesso.", data=data)


@router.post(
    "/guardian-links/{link_id}/consent",
    response_model=ApiResponse[GuardianLinkConsentItem],
    summary="Autoriza um responsável a acompanhar sua jornada",
)
async def consent_guardian_link(
    link_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianLinkConsentItem]:
    data = await guardian_consent_service.grant_consent(db, current_user, link_id)
    return ApiResponse(success=True, message="Vínculo autorizado com sucesso.", data=data)


@router.post(
    "/guardian-links/{link_id}/revoke",
    response_model=ApiResponse[GuardianLinkConsentItem],
    summary="Revoga o acesso de um responsável já autorizado",
)
async def revoke_guardian_link(
    link_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianLinkConsentItem]:
    data = await guardian_consent_service.revoke_consent(db, current_user, link_id)
    return ApiResponse(success=True, message="Vínculo revogado com sucesso.", data=data)
