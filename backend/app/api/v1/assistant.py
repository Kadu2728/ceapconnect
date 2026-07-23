"""Router do Assistente IA (EPIC 11).

Rotas protegidas via `Depends(get_current_user)`. O `POST /chat` responde em
*streaming* de texto puro (não envelopado) — o frontend renderiza os tokens
conforme chegam. A regra de negócio vive em `app.services.assistant_service`.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import ChatHistory, ChatRequest
from app.schemas.response import ApiResponse
from app.services import assistant_service

router = APIRouter(prefix="/assistant", tags=["Assistente"])


@router.get(
    "/history",
    response_model=ApiResponse[ChatHistory],
    summary="Histórico da conversa com o assistente",
)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ChatHistory]:
    """Retorna as mensagens trocadas entre o candidato e o assistente."""
    data = await assistant_service.get_history(db, current_user)
    return ApiResponse(success=True, message="Histórico recuperado com sucesso.", data=data)


@router.post(
    "/chat",
    summary="Conversa com o assistente (resposta em streaming de texto)",
)
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Envia uma mensagem ao assistente e transmite a resposta em streaming."""
    generator = assistant_service.stream_chat(db, current_user, payload.message)
    return StreamingResponse(generator, media_type="text/plain; charset=utf-8")
