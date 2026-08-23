"""Router do funil de conversão da jornada (KPI inscrição→prova).

Mesmo escopo do Console de Intervenção: coordenador vê apenas a própria
coorte, admin vê todas (`app.core.rbac.CohortScope`).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CohortScope, get_cohort_scope
from app.core.database import get_db
from app.schemas.funnel import FunnelResponse
from app.schemas.response import ApiResponse
from app.services import funnel_service

router = APIRouter(tags=["Funil de Conversão"])


@router.get(
    "/admin/funnel",
    response_model=ApiResponse[FunnelResponse],
    summary="Funil de conversão da jornada, com destaque para inscrição→prova",
)
async def get_funnel(
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FunnelResponse]:
    """Contagem e taxa de queda por etapa, dentro do escopo do usuário."""
    data = await funnel_service.get_funnel(db, cohort_ids=scope.cohort_ids)
    return ApiResponse(
        success=True, message="Funil de conversão recuperado com sucesso.", data=data
    )
