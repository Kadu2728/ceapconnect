"""Schemas de request/response da feature Missões (EPIC 05).

Espelham o contrato consumido pelo frontend (`features/missions`). O status e
a data de conclusão vêm de `MissionProgress`; os demais campos, de `Mission`.
Por isso `MissionItem` é montado explicitamente no service, não via
`from_attributes` sobre uma única entidade.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MissionItem(BaseModel):
    """Uma missão do candidato com o respectivo progresso."""

    id: uuid.UUID
    title: str
    description: str
    xp_reward: int
    due_date: date | None
    status: str
    completed_at: datetime | None


class MissionSummary(BaseModel):
    """Resumo do progresso do candidato em missões."""

    total: int
    completed: int
    xp_total: int


class MissionListResponse(BaseModel):
    """Corpo de `GET /api/v1/missions`."""

    missions: list[MissionItem]
    summary: MissionSummary


class UnlockedAchievement(BaseModel):
    """Conquista desbloqueada como efeito da conclusão de uma missão."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str
    icon: str


class CompleteMissionResponse(BaseModel):
    """Corpo de `POST /api/v1/missions/{id}/complete`."""

    mission: MissionItem
    xp_gained: int
    xp_total: int
    unlocked_achievements: list[UnlockedAchievement]
