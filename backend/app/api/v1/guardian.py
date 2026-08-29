"""Router do RBAC do responsável (conta própria, autenticada).

Protegido por `Depends(get_current_guardian)` + `Depends(get_guardian_scope)`
— nunca por `get_current_user` puro. Distinto de `app.api.v1.guardian_portal`
(público, link mágico, sem conta): aqui é sempre uma sessão de verdade,
como qualquer outra rota autenticada do produto.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import GuardianScope, get_guardian_scope
from app.core.database import get_db
from app.schemas.guardian_access import GuardianChildJourneyResponse, GuardianChildrenResponse
from app.schemas.response import ApiResponse
from app.services import guardian_access_service

router = APIRouter(prefix="/guardian", tags=["RBAC do Responsável"])


@router.get(
    "/children",
    response_model=ApiResponse[GuardianChildrenResponse],
    summary="Filhos vinculados e autorizados à conta do responsável",
)
async def list_children(
    scope: GuardianScope = Depends(get_guardian_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianChildrenResponse]:
    data = await guardian_access_service.list_children(db, scope)
    return ApiResponse(success=True, message="Filhos recuperados com sucesso.", data=data)


@router.get(
    "/children/{candidate_profile_id}/journey",
    response_model=ApiResponse[GuardianChildJourneyResponse],
    summary="Jornada essencial de um filho — nunca inclui score de risco",
)
async def get_child_journey(
    candidate_profile_id: uuid.UUID,
    scope: GuardianScope = Depends(get_guardian_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianChildJourneyResponse]:
    data = await guardian_access_service.get_child_journey(db, scope, candidate_profile_id)
    return ApiResponse(success=True, message="Jornada recuperada com sucesso.", data=data)
