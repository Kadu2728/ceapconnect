"""Model SQLAlchemy da entidade `RiskScoreHistory` (EPIC 14 — fase 2 do moat).

Série histórica **append-only** dos scores de risco: uma linha por
recálculo, nunca sobrescrita — ao contrário de `RiskScore`
(`app.models.risk_score`), que guarda só o estado *atual*. É a base de dados
que faltava para o harness de backtest (precision/recall/F1/AUC) comparar o
score que um candidato tinha no passado contra o outcome real que ele teve
depois (`CandidateProfile.status`).

Índice `(candidate_profile_id, computed_at)`: o backtest sempre lê "a série
de scores deste candidato ao longo do tempo" — mesmo racional de
`app.models.activity_event.ActivityEvent`.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.risk_scoring import RiskTier


class RiskScoreHistory(Base):
    """Um snapshot imutável do score de um candidato em um recálculo específico."""

    __tablename__ = "risk_score_history"
    __table_args__ = (
        Index(
            "ix_risk_score_history_candidate_computed",
            "candidate_profile_id",
            "computed_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    tier: Mapped[RiskTier] = mapped_column(String(10), nullable=False)
    factors: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, server_default="[]", nullable=False
    )
    explanation: Mapped[str] = mapped_column(String(500), nullable=False)
    features: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}", nullable=False
    )
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<RiskScoreHistory candidate_profile_id={self.candidate_profile_id} "
            f"score={self.score} computed_at={self.computed_at}>"
        )
