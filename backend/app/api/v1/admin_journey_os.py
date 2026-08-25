"""Router de métricas do Candidate Journey OS (fase F2 — Learning Loop).

Admin-only (`get_current_admin`, não `CohortScope`): CTR do Next Best
Action e taxa de retomada do Modo Resgate são métricas de saúde do
produto como um todo, não dado operacional por coorte — diferente do
Console de Intervenção e do Funil, que são escopados por coordenador.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.journey_os_metrics import JourneyOsMetricsResponse
from app.schemas.response import ApiResponse
from app.services import journey_os_metrics_service

router = APIRouter(tags=["Candidate Journey OS"])


@router.get(
    "/admin/journey-os/metrics",
    response_model=ApiResponse[JourneyOsMetricsResponse],
    summary="Métricas do Learning Loop (CTR do Next Best Action, conversão do Modo Resgate)",
)
async def get_journey_os_metrics(
    window_days: int = Query(default=30, ge=1, le=365),
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[JourneyOsMetricsResponse]:
    """Contagens e taxas de conversão do NBA e do Modo Resgate no período."""
    data = await journey_os_metrics_service.get_metrics(db, window_days=window_days)
    return ApiResponse(success=True, message="Métricas recuperadas com sucesso.", data=data)
