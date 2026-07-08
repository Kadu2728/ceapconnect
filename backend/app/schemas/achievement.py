"""Schemas de response da feature Conquistas (EPIC 06).

Espelham o contrato consumido pelo frontend (`features/achievements`). Cada
item traz o catálogo global com o status (desbloqueada ou não) do candidato.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class AchievementItem(BaseModel):
    """Uma conquista do catálogo com o status de desbloqueio do candidato."""

    id: uuid.UUID
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: datetime | None


class AchievementSummary(BaseModel):
    """Resumo das conquistas do candidato."""

    total: int
    unlocked: int


class AchievementListResponse(BaseModel):
    """Corpo de `GET /api/v1/achievements`."""

    achievements: list[AchievementItem]
    summary: AchievementSummary
