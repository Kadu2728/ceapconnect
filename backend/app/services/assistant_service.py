"""Regra de negócio do Assistente IA (EPIC 11).

O assistente responde dúvidas dos alunos sobre o processo seletivo do CEAP e
sobre o próprio app (missões, conquistas, eventos, jornada). Usa a API do
**Google Gemini** (mesmo provider e modelo do projeto VendIA) com streaming de
resposta, consumida via `httpx` sobre o endpoint `streamGenerateContent` (SSE) —
assim não dependemos de detalhes de versão de SDK. Mantém o histórico da
conversa por candidato no banco (multi-turn real).

Degradação graciosa: se a chave não estiver configurada, o endpoint continua
funcionando — responde com uma mensagem clara de "não configurado" e persiste
a conversa — para a feature estar pronta e passar a responder de verdade assim
que a chave for adicionada ao `.env`.
"""

import json
import logging
import uuid
from collections.abc import AsyncGenerator

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.chat_message import ROLE_ASSISTANT, ROLE_USER
from app.models.user import User
from app.repositories.chat_message_repository import ChatMessageRepository
from app.schemas.chat import ChatHistory, ChatMessageItem
from app.services.candidate_profile_service import get_profile_or_raise

logger = logging.getLogger("ceap_connect.assistant")

# Endpoint de streaming (SSE) da API do Gemini. `{model}` é interpolado a partir
# das settings; a chave vai no header `x-goog-api-key` (nunca na URL).
_GEMINI_STREAM_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse"
)

_SYSTEM_PROMPT = (
    "Você é o assistente virtual do CEAP Connect, o app que acompanha a jornada "
    "dos candidatos no processo seletivo do CEAP — Centro Educacional Assistencial "
    "Profissionalizante, uma escola técnica gratuita em São Paulo (bairro da "
    "Pedreira), com cerca de 40 anos de história.\n\n"
    "Seu público são jovens de 14 a 18 anos. Fale em português do Brasil, de forma "
    "acolhedora, clara e motivadora, sem ser infantil. Respostas curtas e diretas.\n\n"
    "Você pode ajudar com:\n"
    "- Dúvidas sobre o processo seletivo (inscrição online, prova de Português e "
    "Matemática, e entrevista com o responsável). A seleção é 100% gratuita.\n"
    "- Os cursos técnicos gratuitos: Administração, Informática, Redes de "
    "Computadores e Cinema e Audiovisual.\n"
    "- Como usar o app: jornada, missões (ganham XP), conquistas, eventos e "
    "notificações.\n"
    "- Dicas de estudo e organização para o dia da prova.\n\n"
    "Regras importantes:\n"
    "- Nunca invente datas, valores, notas de corte ou regras específicas do edital. "
    "Se não tiver certeza, diga com honestidade que não sabe e oriente o aluno a "
    "confirmar no site oficial (ceappedreira.org.br) ou com a secretaria do CEAP.\n"
    "- Mantenha o foco no CEAP e no processo seletivo. Se perguntarem algo fora "
    "desse escopo, responda brevemente e redirecione com gentileza.\n"
    "- Nunca peça senhas, CPF completo ou dados sensíveis."
)

_NOT_CONFIGURED_MESSAGE = (
    "O assistente de IA ainda não foi ativado por aqui. Peça ao administrador do "
    "CEAP Connect para configurar o acesso. Enquanto isso, você pode explorar suas "
    "missões, conquistas e eventos pelo menu. 😉"
)

_ERROR_MESSAGE = (
    "Desculpe, tive um problema para responder agora. Tente novamente em alguns instantes."
)


def is_configured() -> bool:
    """Indica se a chave da API do Gemini está configurada."""
    return bool(settings.gemini_api_key.strip())


async def get_history(db: AsyncSession, user: User) -> ChatHistory:
    """Retorna o histórico de conversa do candidato com o assistente."""
    profile = await get_profile_or_raise(db, user)
    rows = await ChatMessageRepository(db).list_for_profile(profile.id)

    return ChatHistory(
        messages=[
            ChatMessageItem(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message in rows
        ],
        configured=is_configured(),
    )


async def stream_chat(db: AsyncSession, user: User, message: str) -> AsyncGenerator[str]:
    """Gera a resposta do assistente em streaming (tokens conforme chegam).

    Persiste a mensagem do usuário antes de responder e a resposta completa do
    assistente ao final — garantindo um histórico multi-turn consistente.
    """
    profile = await get_profile_or_raise(db, user)
    repo = ChatMessageRepository(db)

    await repo.create(candidate_profile_id=profile.id, role=ROLE_USER, content=message)
    await db.commit()

    if not is_configured():
        yield _NOT_CONFIGURED_MESSAGE
        await _persist_assistant(repo, db, profile.id, _NOT_CONFIGURED_MESSAGE)
        return

    history = await repo.list_for_profile(profile.id)
    # Formato Gemini: o prompt de sistema vai em `system_instruction` (separado);
    # o histórico vira `contents` com roles "user"/"model".
    contents = [_to_gemini_content(row.role, row.content) for row in history]

    collected: list[str] = []
    try:
        async for text in _stream_gemini(contents):
            collected.append(text)
            yield text
    except Exception:  # noqa: BLE001 — qualquer falha vira uma resposta amigável
        logger.exception("Falha ao gerar resposta do assistente (Gemini)")
        if not collected:
            collected.append(_ERROR_MESSAGE)
            yield _ERROR_MESSAGE
    finally:
        full_reply = "".join(collected).strip()
        if full_reply:
            await _persist_assistant(repo, db, profile.id, full_reply)


def _to_gemini_content(role: str, text: str) -> dict:
    """Converte uma mensagem do histórico no formato de `contents` do Gemini.

    O Gemini usa os papéis "user" e "model" (não "assistant"); tudo que não for
    do usuário é tratado como resposta do modelo.
    """
    gemini_role = "user" if role == ROLE_USER else "model"
    return {"role": gemini_role, "parts": [{"text": text}]}


async def _stream_gemini(contents: list[dict]) -> AsyncGenerator[str]:
    """Streama a resposta do Gemini (SSE), emitindo cada trecho de texto."""
    url = _GEMINI_STREAM_URL.format(model=settings.gemini_model)
    headers = {"x-goog-api-key": settings.gemini_api_key}
    body = {
        "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": settings.assistant_max_tokens},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, headers=headers, json=body) as response:
            if response.status_code != 200:
                detail = (await response.aread()).decode("utf-8", "replace")
                logger.error("Gemini %s: %s", response.status_code, detail[:600])
                response.raise_for_status()

            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                payload = line[len("data:") :].strip()
                if not payload:
                    continue
                data = json.loads(payload)
                for candidate in data.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        text = part.get("text")
                        if text:
                            yield text


async def _persist_assistant(
    repo: ChatMessageRepository, db: AsyncSession, profile_id: uuid.UUID, content: str
) -> None:
    """Salva a resposta do assistente e commita."""
    await repo.create(candidate_profile_id=profile_id, role=ROLE_ASSISTANT, content=content)
    await db.commit()
