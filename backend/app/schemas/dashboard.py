"""Schemas Pydantic do agregado de `GET /api/v1/dashboard` (EPIC 03).

Único endpoint de leitura que compõe dados de várias entidades (jornada,
missões, conquistas, eventos, notificações) num único payload consumido
pelo Dashboard do frontend.
"""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

JourneyStepStatus = Literal["completed", "current", "pending"]


class JourneyStepItem(BaseModel):
    """Uma etapa da timeline da jornada, já com o status do candidato."""

    key: str
    label: str
    status: JourneyStepStatus


class JourneyProgress(BaseModel):
    """Progresso do candidato na jornada."""

    percentage: int
    current_step_key: str
    steps: list[JourneyStepItem]


class NextMission(BaseModel):
    """Próxima missão pendente do candidato."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    xp_reward: int
    due_date: date | None


class RecentAchievement(BaseModel):
    """Conquista recentemente desbloqueada pelo candidato."""

    id: uuid.UUID
    name: str
    description: str
    icon: str
    unlocked_at: datetime


class UpcomingEvent(BaseModel):
    """Evento futuro disponível para o candidato."""

    id: uuid.UUID
    title: str
    date: datetime
    location: str


class DashboardResponse(BaseModel):
    """Dado agregado retornado por `GET /api/v1/dashboard`."""

    greeting_name: str
    journey: JourneyProgress
    xp_total: int
    next_mission: NextMission | None
    recent_achievements: list[RecentAchievement]
    upcoming_events: list[UpcomingEvent]
    unread_notifications_count: int
    exam_date: date | None
