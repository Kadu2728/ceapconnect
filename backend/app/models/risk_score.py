"""Model SQLAlchemy da entidade `RiskScore` (EPIC 14 — Predição de evasão).

Estado **atual** do risco de cada candidato — uma linha por candidato,
sobrescrita a cada recálculo (não é histórico append-only; ver
`app.models.risk_score_history.RiskScoreHistory` para a série temporal, e
`app.models.intervention.Intervention.score_at_creation` para a comparação
"antes/depois" usada na medição de impacto de uma intervenção).

`factors` guarda a decomposição do score (lista de `{key, label, points}`) e
`features` guarda o snapshot das features usadas — útil tanto para auditoria
quanto como futura base de treino se o score heurístico for substituído por um
modelo aprendido.
"""

import uuid
from datetime import datetime
from typing import Any, Final

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.risk_scoring import RiskTier

_VALID_TIERS: Final = ("baixo", "medio", "alto")


class RiskScore(Base):
    """Score de evasão atual de um candidato (upsert por `candidate_profile_id`)."""

    __tablename__ = "risk_scores"
    __table_args__ = (CheckConstraint(f"tier IN {_VALID_TIERS}", name="ck_risk_score_tier"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    tier: Mapped[RiskTier] = mapped_column(String(10), index=True, nullable=False)
    # Decomposição do score: [{"key": "inactivity", "label": "...", "points": 12.3}, ...]
    factors: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, server_default="[]", nullable=False
    )
    # Texto pronto para UI, já montado pela camada de domínio (RiskScoreResult.explanation).
    explanation: Mapped[str] = mapped_column(String(500), nullable=False)
    # Snapshot das features usadas neste cálculo (auditoria + base de treino futura).
    features: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}", nullable=False
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    # Qual implementação de `RiskScorer` gerou este score (ver
    # `app.core.risk_scoring.RiskScorer.model_version`) — permite comparar
    # heurística vs. modelo treinado no harness de backtest sem ambiguidade
    # sobre qual gerou qual número.
    model_version: Mapped[str] = mapped_column(
        String(50), default="heuristic-v1", server_default="heuristic-v1", nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<RiskScore candidate_profile_id={self.candidate_profile_id} "
            f"score={self.score} tier={self.tier}>"
        )
