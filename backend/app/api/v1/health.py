"""Router de health check.

Apenas orquestra request/response — toda a lógica está em
`app.services.health_service`.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.health import HealthData
from app.schemas.response import ApiResponse
from app.services.health_service import get_health_status

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ApiResponse[HealthData])
async def health_check(db: AsyncSession = Depends(get_db)) -> ApiResponse[HealthData]:
    """Retorna o status da aplicação e da conexão com o banco de dados."""
    data = await get_health_status(db)
    return ApiResponse(success=True, message="Aplicação operante.", data=data)
