"""Router do Candidate State (Candidate Journey OS — fase N1).

Rota protegida via `Depends(get_current_user)`, mesmo padrão do Dashboard —
retorna sempre o estado do próprio candidato autenticado, nunca de terceiros
(isso é papel do Console de Intervenção, atrás de `CohortScope`).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.candidate_state import CandidateStateResponse, TrackEventRequest
from app.schemas.response import ApiResponse
from app.services import candidate_state_service

router = APIRouter(prefix="/candidate-state", tags=["Candidate Journey OS"])


@router.get(
    "",
    response_model=ApiResponse[CandidateStateResponse],
    summary="Estado computado da jornada do candidato autenticado",
)
async def get_candidate_state(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CandidateStateResponse]:
    """Retorna o `momentum` e os sinais que alimentam Next Best Action e Recovery."""
    data = await candidate_state_service.get_candidate_state(db, current_user)
    return ApiResponse(
        success=True, message="Estado do candidato recuperado com sucesso.", data=data
    )


@router.post(
    "/events",
    response_model=ApiResponse[None],
    status_code=status.HTTP_201_CREATED,
    summary="Registra um evento do Candidate Journey OS disparado pelo cliente",
)
async def track_candidate_event(
    payload: TrackEventRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Best-effort (mesma garantia de `activity_event_service`): nunca falha
    de um jeito que quebre a experiência do candidato por causa de telemetria."""
    await candidate_state_service.track_client_event(
        db, current_user, name=payload.name, props=payload.props
    )
    return ApiResponse(success=True, message="Evento registrado.", data=None)
