"""Schemas Pydantic do agregado de `GET /api/v1/dashboard` (EPIC 03).

Único endpoint de leitura que compõe dados de várias entidades (jornada,
missões, conquistas, eventos, notificações) num único payload consumido
pelo Dashboard do frontend.
"""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.gamification import LevelInfo

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


class NextReward(BaseModel):
    """Recompensa em destaque no Dashboard (a "próxima" a mirar ou resgatar)."""

    id: uuid.UUID
    title: str
    provider: str
    icon: str
    # available = já desbloqueada (pode resgatar agora); locked = ainda a conquistar.
    status: Literal["available", "locked"]
    requirement_label: str


class CohortStanding(BaseModel):
    """Faixa de engajamento do candidato na coorte (EPIC 20).

    Nunca carrega posição exata nem identidade de outros candidatos — só a
    faixa ampla e o tamanho da turma. Ver `cohort_stats_service`.
    """

    cohort_size: int
    # 10/25/50 = "entre os N% mais engajados"; None = fora do top 50 (a
    # mensagem vira progresso pessoal, nunca "você está entre os piores").
    top_percent: int | None
    message: str


class DashboardResponse(BaseModel):
    """Dado agregado retornado por `GET /api/v1/dashboard`."""

    greeting_name: str
    journey: JourneyProgress
    xp_total: int
    # Nível atual do candidato e progresso rumo ao próximo (gamificação — EPIC 13).
    level: LevelInfo
    # Recompensa em destaque (a resgatar ou a mirar); None se não houver.
    next_reward: NextReward | None
    next_mission: NextMission | None
    recent_achievements: list[RecentAchievement]
    upcoming_events: list[UpcomingEvent]
    unread_notifications_count: int
    exam_date: date | None
    # False = candidato ainda não viu a tela de boas-vindas (primeiro login).
    onboarded: bool
    # None = coorte inexistente/pequena demais para ser anônima (EPIC 20).
    cohort_standing: CohortStanding | None
