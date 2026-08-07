"""Schemas de response do painel administrativo (EPIC 10 + EPIC 13)."""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class DailyCount(BaseModel):
    """Contagem de um dia (série para gráfico)."""

    date: date
    count: int


class LevelBucket(BaseModel):
    """Quantos alunos estão em cada nível (distribuição de progressão)."""

    level: int
    name: str
    count: int


class TopReward(BaseModel):
    """Uma recompensa no ranking das mais resgatadas."""

    title: str
    provider: str
    count: int


class InterventionImpact(BaseModel):
    """Impacto das intervenções do Console de Evasão nos últimos 30 dias (EPIC 14).

    Fecha o loop "esforço → contato → resultado": mede se as intervenções dos
    coordenadores estão de fato reduzindo o risco. Campos `None` = ainda não
    há nenhuma intervenção medida no período (menos de 7 dias desde a 1ª).
    """

    total: int
    measured: int
    pending_measurement: int
    # Negativo = risco caiu em média (bom sinal).
    avg_score_delta: float | None
    pct_improved: float | None
    pct_had_activity_after: float | None


class AdminOverview(BaseModel):
    """Visão geral de métricas da plataforma (`GET /api/v1/admin/overview`)."""

    total_students: int
    accessed: int
    never_accessed: int
    engagement_rate: float
    active_24h: int
    active_7d: int
    active_30d: int
    new_7d: int
    new_30d: int
    missions_completed: int
    event_registrations: int
    # Gamificação (EPIC 13).
    achievements_unlocked: int
    total_xp: int
    avg_xp: int
    rewards_redeemed: int
    rewards_pending: int
    rewards_fulfilled: int
    level_distribution: list[LevelBucket]
    top_rewards: list[TopReward]
    signups_daily: list[DailyCount]
    # Predição de evasão (EPIC 14).
    intervention_impact: InterventionImpact


class AdminRedemptionItem(BaseModel):
    """Um resgate de recompensa na fila de entrega do admin (EPIC 13)."""

    id: uuid.UUID
    student_name: str
    student_email: str
    reward_title: str
    reward_provider: str
    status: Literal["pending", "fulfilled", "cancelled"]
    redeemed_at: datetime
    fulfilled_at: datetime | None


class AdminRedemptionListResponse(BaseModel):
    """Fila de resgates (`GET /api/v1/admin/redemptions`), com resumo por status."""

    redemptions: list[AdminRedemptionItem]
    pending_count: int
    fulfilled_count: int
