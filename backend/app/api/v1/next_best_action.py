"""Router do Next Best Action Engine (Candidate Journey OS — fase N2).

Rota protegida via `Depends(get_current_user)`, mesmo padrão do Dashboard e
do Candidate State — sempre a recomendação do próprio candidato autenticado.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.next_best_action import NextBestActionResponse
from app.schemas.response import ApiResponse
from app.services import next_best_action_service

router = APIRouter(prefix="/next-best-action", tags=["Candidate Journey OS"])


@router.get(
    "",
    response_model=ApiResponse[NextBestActionResponse | None],
    summary="Próxima ação recomendada para o candidato autenticado",
)
async def get_next_best_action(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NextBestActionResponse | None]:
    """Retorna a ação única recomendada agora, ou `data=null` se nada for acionável."""
    action = await next_best_action_service.get_next_best_action(db, current_user)
    data = (
        NextBestActionResponse(
            action_key=action.action_key, cta_label=action.cta_label, why=action.why
        )
        if action is not None
        else None
    )
    message = (
        "Próxima ação recomendada recuperada com sucesso."
        if action is not None
        else "Nenhuma ação recomendada no momento."
    )
    return ApiResponse(success=True, message=message, data=data)
