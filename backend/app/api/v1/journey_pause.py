"""Router da Pausa Declarada ("Jornada que Respira" — fase 1).

Protegido por `Depends(get_current_user)` — sempre a pausa do próprio
candidato autenticado, nunca de terceiros. O coordenador enxerga pausas pelo
Console de Intervenção (leitura, atrás de `CohortScope`), nunca por aqui.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.journey_pause import PauseResumeResult, PauseStartRequest, PauseState
from app.schemas.response import ApiResponse
from app.services import journey_pause_service

router = APIRouter(prefix="/candidate", tags=["Jornada que Respira"])


@router.post(
    "/pause",
    response_model=ApiResponse[PauseState],
    summary="Candidato declara uma pausa curta na jornada",
)
async def start_pause(
    payload: PauseStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PauseState]:
    data = await journey_pause_service.start_pause(db, current_user, payload)
    return ApiResponse(success=True, message="Guardamos seu lugar.", data=data)


@router.post(
    "/pause/resume",
    response_model=ApiResponse[PauseResumeResult],
    summary="Candidato retoma a jornada de onde parou",
)
async def resume_pause(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PauseResumeResult]:
    data = await journey_pause_service.resume_pause(db, current_user)
    return ApiResponse(success=True, message="Bom te ver de volta.", data=data)
