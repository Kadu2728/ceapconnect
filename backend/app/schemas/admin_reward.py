"""Schemas do CRUD de recompensas no painel admin (EPIC 13 — gestão).

Permite ao CEAP criar/editar/ativar recompensas pelo painel, sem depender de
seed/DB. A validação garante a coerência da condição de desbloqueio: por nível
exige `required_level` válido; por conquista exige `required_achievement_id`.
"""

import uuid
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.core.gamification import LEVEL_TIERS

RewardUnlockType = Literal["level", "achievement"]

_MAX_LEVEL = len(LEVEL_TIERS)


class AdminAchievementOption(BaseModel):
    """Opção de conquista para o seletor de gatilho no formulário."""

    id: uuid.UUID
    name: str


class AdminRewardItem(BaseModel):
    """Uma recompensa na visão de gestão (inclui inativas e o gatilho por nome)."""

    id: uuid.UUID
    title: str
    description: str
    provider: str
    category: str
    icon: str
    unlock_type: RewardUnlockType
    required_level: int | None
    required_achievement_id: uuid.UUID | None
    required_achievement_name: str | None
    featured: bool
    is_active: bool
    sort_order: int


class AdminRewardListResponse(BaseModel):
    """Payload de `GET /api/v1/admin/rewards` (catálogo + conquistas p/ seletor)."""

    rewards: list[AdminRewardItem]
    achievements: list[AdminAchievementOption]


class AdminRewardWrite(BaseModel):
    """Corpo de criação/edição de recompensa (`POST`/`PATCH /admin/rewards`).

    Envio completo dos campos editáveis (não parcial): simplifica a validação da
    condição de desbloqueio e o formulário do frontend sempre manda o objeto todo.
    """

    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=2, max_length=2000)
    provider: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    icon: str = Field(min_length=1, max_length=50)
    unlock_type: RewardUnlockType
    required_level: int | None = Field(default=None, ge=1, le=_MAX_LEVEL)
    required_achievement_id: uuid.UUID | None = None
    featured: bool = False
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _check_unlock_condition(self) -> "AdminRewardWrite":
        """Garante que a condição de desbloqueio bate com o `unlock_type`."""
        if self.unlock_type == "level":
            if self.required_level is None:
                raise ValueError("Recompensa por nível exige 'required_level'.")
            # Ignora um id de conquista eventualmente enviado por engano.
            self.required_achievement_id = None
        else:  # achievement
            if self.required_achievement_id is None:
                raise ValueError("Recompensa por conquista exige 'required_achievement_id'.")
            self.required_level = None
        return self
