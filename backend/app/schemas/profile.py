"""Schemas Pydantic da Tela de Perfil (EPIC 09).

Compõe os dados cadastrais do usuário com um resumo de gamificação (nível, XP e
contadores). Dados sensíveis: o CPF é retornado **mascarado** (nunca completo).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.gamification import LevelInfo


class ProfileStats(BaseModel):
    """Resumo de gamificação do candidato exibido no perfil."""

    level: LevelInfo
    missions_completed: int
    achievements_unlocked: int
    rewards_redeemed: int


class ProfileResponse(BaseModel):
    """Payload de `GET /api/v1/profile`."""

    id: uuid.UUID
    name: str
    email: str
    # CPF mascarado (ex.: "123.***.***-09") — nunca o número completo.
    cpf_masked: str
    phone: str
    member_since: datetime
    stats: ProfileStats


class ProfileUpdateRequest(BaseModel):
    """Campos editáveis do perfil (`PATCH /api/v1/profile`)."""

    name: str = Field(min_length=2, max_length=150)
    # Telefone só com dígitos (DDD + número): 10 ou 11 dígitos.
    phone: str = Field(min_length=10, max_length=11)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 2:
            raise ValueError("Nome muito curto.")
        return stripped

    @field_validator("phone")
    @classmethod
    def _digits_only(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) not in (10, 11):
            raise ValueError("Telefone deve ter 10 ou 11 dígitos (DDD + número).")
        return digits
