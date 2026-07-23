"""Schemas da feature Assistente IA (EPIC 11).

A resposta do chat é enviada como *stream* de texto (não envelopada), por isso
aqui só definimos o corpo da requisição e o histórico (`GET`).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageItem(BaseModel):
    """Uma mensagem do histórico de conversa com o assistente."""

    id: uuid.UUID
    role: str
    content: str
    created_at: datetime


class ChatHistory(BaseModel):
    """Corpo de `GET /api/v1/assistant/history`."""

    messages: list[ChatMessageItem]
    configured: bool


class ChatRequest(BaseModel):
    """Corpo de `POST /api/v1/assistant/chat`."""

    message: str = Field(min_length=1, max_length=2000)
