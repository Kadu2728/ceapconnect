"""Router dos Simulados de prova (EPIC 16).

Rotas protegidas via `Depends(get_current_user)`. Toda a regra de negócio
(sorteio de questões, correção, XP, histórico) vive em
`app.services.simulado_service` — o router apenas orquestra e envelopa.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.simulado import (
    AnswerRequest,
    AnswerResult,
    AttemptHistoryResponse,
    FinishAttemptResponse,
    StartAttemptResponse,
)
from app.services import simulado_service

router = APIRouter(prefix="/simulados", tags=["Simulados"])


@router.post(
    "/start",
    response_model=ApiResponse[StartAttemptResponse],
    summary="Inicia um novo simulado (10 questões de Português + 10 de Matemática)",
)
async def start_attempt(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[StartAttemptResponse]:
    """Sorteia as questões e abre a tentativa. Nunca inclui a resposta certa."""
    data = await simulado_service.start_attempt(db, current_user)
    return ApiResponse(success=True, message="Simulado iniciado com sucesso.", data=data)


@router.post(
    "/{attempt_id}/answer",
    response_model=ApiResponse[AnswerResult],
    summary="Responde uma questão do simulado",
)
async def answer_question(
    attempt_id: uuid.UUID,
    payload: AnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AnswerResult]:
    """Registra a resposta e devolve o feedback imediato (certo/errado + explicação)."""
    data = await simulado_service.answer_question(db, current_user, attempt_id, payload)
    return ApiResponse(success=True, message="Resposta registrada.", data=data)


@router.post(
    "/{attempt_id}/finish",
    response_model=ApiResponse[FinishAttemptResponse],
    summary="Finaliza o simulado e apura o resultado",
)
async def finish_attempt(
    attempt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FinishAttemptResponse]:
    """Fecha a tentativa, calcula o placar e concede o XP do simulado."""
    data = await simulado_service.finish_attempt(db, current_user, attempt_id)
    return ApiResponse(success=True, message="Simulado concluído com sucesso.", data=data)


@router.get(
    "/history",
    response_model=ApiResponse[AttemptHistoryResponse],
    summary="Histórico pessoal de simulados",
)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AttemptHistoryResponse]:
    """Tentativas já concluídas do candidato, mais recentes primeiro."""
    data = await simulado_service.get_history(db, current_user)
    return ApiResponse(success=True, message="Histórico recuperado com sucesso.", data=data)
