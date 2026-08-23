"""Router do responsável — alvo duplo do Console de Intervenção + Área de Pais.

Mesmo escopo de `admin_risk.py`: `Depends(get_cohort_scope)` em toda rota —
coordenador vê só a própria coorte, admin vê todas. Nunca exposto a
candidatos.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CohortScope, get_cohort_scope
from app.core.database import get_db
from app.schemas.guardian import (
    CohortTrainingDateUpdateRequest,
    GuardianInterventionCreateRequest,
    GuardianInterventionItem,
    GuardianMilestoneItem,
    GuardiansAtRiskResponse,
)
from app.schemas.response import ApiResponse
from app.services import guardian_service

router = APIRouter(tags=["Responsáveis"])


@router.get(
    "/admin/guardians/at-risk",
    response_model=ApiResponse[GuardiansAtRiskResponse],
    summary="Famílias que precisam de atenção com a formação obrigatória",
)
async def get_guardians_at_risk(
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardiansAtRiskResponse]:
    data = await guardian_service.get_at_risk(db, scope)
    return ApiResponse(
        success=True, message="Responsáveis em risco recuperados com sucesso.", data=data
    )


@router.post(
    "/admin/guardians/interventions",
    response_model=ApiResponse[GuardianInterventionItem],
    status_code=201,
    summary="Registra um contato com o responsável",
)
async def create_guardian_intervention(
    payload: GuardianInterventionCreateRequest,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianInterventionItem]:
    data = await guardian_service.create_intervention(db, scope, payload)
    return ApiResponse(success=True, message="Intervenção registrada com sucesso.", data=data)


@router.post(
    "/admin/guardians/{guardian_id}/training-confirmed",
    response_model=ApiResponse[GuardianMilestoneItem],
    summary="Marca que o responsável confirmou presença na formação",
)
async def mark_training_confirmed(
    guardian_id: uuid.UUID,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianMilestoneItem]:
    data = await guardian_service.mark_training_confirmed(db, scope, guardian_id)
    return ApiResponse(success=True, message="Confirmação registrada com sucesso.", data=data)


@router.post(
    "/admin/guardians/{guardian_id}/training-attended",
    response_model=ApiResponse[GuardianMilestoneItem],
    summary="Marca presença do responsável na formação obrigatória",
)
async def mark_training_attended(
    guardian_id: uuid.UUID,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GuardianMilestoneItem]:
    """Zera o risco do responsável e desbloqueia o marco simbólico na jornada do candidato."""
    data = await guardian_service.mark_training_attended(db, scope, guardian_id)
    return ApiResponse(success=True, message="Presença registrada com sucesso.", data=data)


@router.patch(
    "/admin/cohorts/{cohort_id}/guardian-training-date",
    response_model=ApiResponse[None],
    summary="Define a data da formação obrigatória de pais de uma coorte",
)
async def set_cohort_training_date(
    cohort_id: uuid.UUID,
    payload: CohortTrainingDateUpdateRequest,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    await guardian_service.set_cohort_training_date(db, scope, cohort_id, payload)
    return ApiResponse(success=True, message="Data da formação atualizada com sucesso.", data=None)
