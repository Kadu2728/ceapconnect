"""Router do Dashboard do candidato (EPIC 03).

Rota protegida via `Depends(get_current_user)` — nunca faz verificação
manual de token. Agrega jornada, missões, conquistas, eventos e
notificações num único payload; toda a lógica de composição vive em
`app.services.dashboard_service`.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.schemas.response import ApiResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=ApiResponse[DashboardResponse],
    summary="Agregado do Dashboard do candidato",
)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DashboardResponse]:
    """Retorna o agregado de jornada, missões, conquistas, eventos e notificações."""
    data = await dashboard_service.get_dashboard(db, current_user)
    return ApiResponse(success=True, message="Dashboard recuperado com sucesso.", data=data)
