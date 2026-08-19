"""Router do Console de Intervenção (EPIC 14 — Predição de evasão).

Rotas protegidas por `Depends(get_cohort_scope)` — coordenador vê apenas as
próprias coortes, admin vê todas (ver `app.core.rbac.CohortScope`). A regra de
negócio vive em `app.services.risk_service` — o router apenas orquestra e
envelopa.

**Nunca** exposto a candidatos: nenhuma rota aqui é acessível com
`Depends(get_current_user)` puro — todas exigem `get_cohort_scope`, que por
sua vez exige `get_current_coordinator`.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CohortScope, get_cohort_scope
from app.core.database import get_db
from app.core.risk_scoring import RiskTier
from app.schemas.response import ApiResponse
from app.schemas.risk import (
    CandidateRiskDetail,
    CandidateStatusItem,
    CandidateStatusUpdateRequest,
    InterventionCreateRequest,
    InterventionItem,
    RiskQueueResponse,
)
from app.services import risk_service

router = APIRouter(tags=["Predição de Evasão"])


@router.get(
    "/admin/risk/queue",
    response_model=ApiResponse[RiskQueueResponse],
    summary="Fila priorizada de candidatos em risco de evasão",
)
async def get_risk_queue(
    cohort_id: uuid.UUID | None = Query(default=None),
    tier: RiskTier | None = Query(default=None),
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RiskQueueResponse]:
    """Candidatos ordenados do maior para o menor risco, dentro do escopo do usuário."""
    data = await risk_service.get_queue(db, scope, cohort_id=cohort_id, tier=tier)
    return ApiResponse(success=True, message="Fila de risco recuperada com sucesso.", data=data)


@router.get(
    "/admin/candidates/{candidate_profile_id}/risk",
    response_model=ApiResponse[CandidateRiskDetail],
    summary="Detalhe de risco de um candidato",
)
async def get_candidate_risk(
    candidate_profile_id: uuid.UUID,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CandidateRiskDetail]:
    """Score, fatores explicativos, timeline de atividade e histórico de intervenções."""
    data = await risk_service.get_candidate_risk(db, scope, candidate_profile_id)
    return ApiResponse(
        success=True, message="Risco do candidato recuperado com sucesso.", data=data
    )


@router.patch(
    "/admin/candidates/{candidate_profile_id}/status",
    response_model=ApiResponse[CandidateStatusItem],
    summary="Registra o outcome real do candidato (rótulo usado no backtest do modelo de risco)",
)
async def update_candidate_status(
    candidate_profile_id: uuid.UUID,
    payload: CandidateStatusUpdateRequest,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CandidateStatusItem]:
    """Marca aprovado/evadido/desistente — sempre uma ação manual do coordenador.

    A partir daqui o candidato sai do recálculo periódico de risco; o último
    score calculado fica congelado como o valor comparado ao outcome real.
    """
    profile = await risk_service.update_candidate_status(
        db, scope, candidate_profile_id, payload.status
    )
    data = CandidateStatusItem(status=profile.status, status_changed_at=profile.status_changed_at)
    return ApiResponse(success=True, message="Status do candidato atualizado.", data=data)


@router.post(
    "/admin/interventions",
    response_model=ApiResponse[InterventionItem],
    status_code=201,
    summary="Registra uma intervenção com um candidato em risco",
)
async def create_intervention(
    payload: InterventionCreateRequest,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[InterventionItem]:
    """Registra o contato (ligar/WhatsApp/outro) e o resultado imediato."""
    data = await risk_service.create_intervention(db, scope, payload)
    return ApiResponse(success=True, message="Intervenção registrada com sucesso.", data=data)
