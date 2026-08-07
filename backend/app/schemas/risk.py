"""Schemas Pydantic do Console de Intervenção (EPIC 14 — Predição de evasão).

Contrato de:
- `GET  /api/v1/admin/risk/queue`                     → fila priorizada por risco;
- `GET  /api/v1/admin/candidates/{id}/risk`           → detalhe de um candidato;
- `POST /api/v1/admin/interventions`                  → registra um contato;
- `POST /api/v1/internal/risk/recompute`              → dispara o recálculo (API key).

**Regra de negócio embutida no contrato**: nenhum destes schemas é usado por
nenhuma rota candidate-facing — o candidato nunca vê o próprio score
(estigmatizante, ver spec). Só existem sob `/admin` (coordenador/admin) e
`/internal` (API key de serviço).
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, computed_field

from app.core.risk_scoring import RiskTier
from app.models.intervention import InterventionChannel, InterventionOutcome


class RiskFactorItem(BaseModel):
    """Um fator que contribuiu para o score, com o motivo em linguagem humana."""

    key: str
    label: str
    points: float


class RiskQueueItem(BaseModel):
    """Um candidato na fila priorizada de risco."""

    candidate_profile_id: uuid.UUID
    candidate_name: str
    candidate_email: str
    cohort_id: uuid.UUID | None
    cohort_name: str | None
    score: int
    tier: RiskTier
    explanation: str
    computed_at: datetime


class RiskQueueResponse(BaseModel):
    """Payload de `GET /api/v1/admin/risk/queue`."""

    items: list[RiskQueueItem]
    total: int
    counts_by_tier: dict[str, int]


class ActivityTimelineItem(BaseModel):
    """Um evento na linha do tempo de atividade do candidato."""

    name: str
    props: dict[str, Any]
    occurred_at: datetime


class InterventionItem(BaseModel):
    """Uma intervenção registrada, incluindo o resultado da medição de impacto."""

    id: uuid.UUID
    channel: InterventionChannel
    outcome: InterventionOutcome
    notes: str | None
    created_by_name: str | None
    score_at_creation: int
    created_at: datetime
    # Preenchidos ~7 dias depois pelo job (None até lá).
    measured_at: datetime | None
    score_after: int | None
    had_activity_after: bool | None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def score_delta(self) -> int | None:
        """Negativo = risco caiu (bom sinal) desde a intervenção."""
        if self.score_after is None:
            return None
        return self.score_after - self.score_at_creation


class CandidateRiskDetail(BaseModel):
    """Payload de `GET /api/v1/admin/candidates/{id}/risk`."""

    candidate_profile_id: uuid.UUID
    candidate_name: str
    candidate_email: str
    cohort_id: uuid.UUID | None
    cohort_name: str | None
    score: int | None
    tier: RiskTier | None
    factors: list[RiskFactorItem]
    explanation: str | None
    computed_at: datetime | None
    recent_activity: list[ActivityTimelineItem]
    interventions: list[InterventionItem]


class InterventionCreateRequest(BaseModel):
    """Corpo de `POST /api/v1/admin/interventions`."""

    candidate_profile_id: uuid.UUID
    channel: InterventionChannel
    outcome: InterventionOutcome
    notes: str | None = Field(default=None, max_length=1000)


class RecomputeSummary(BaseModel):
    """Payload de `POST /api/v1/internal/risk/recompute`."""

    candidates_processed: int
    interventions_measured: int
    duration_seconds: float
