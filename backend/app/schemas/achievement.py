"""Schemas de response da feature Conquistas (EPIC 06).

Espelham o contrato consumido pelo frontend (`features/achievements`). Cada
item traz o catálogo global com o status (desbloqueada ou não) do candidato.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class AchievementReward(BaseModel):
    """Recompensa atrelada a uma conquista (gancho "conclua → ganhe")."""

    id: uuid.UUID
    title: str
    provider: str


class AchievementItem(BaseModel):
    """Uma conquista do catálogo com o status de desbloqueio do candidato."""

    id: uuid.UUID
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: datetime | None
    # Recompensa que esta conquista desbloqueia (None se não houver).
    reward: AchievementReward | None = None


class AchievementSummary(BaseModel):
    """Resumo das conquistas do candidato."""

    total: int
    unlocked: int


class AchievementListResponse(BaseModel):
    """Corpo de `GET /api/v1/achievements`."""

    achievements: list[AchievementItem]
    summary: AchievementSummary
