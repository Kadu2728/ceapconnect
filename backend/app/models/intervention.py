"""Model SQLAlchemy da entidade `Intervention` (EPIC 14 — Predição de evasão).

Registro de que um coordenador tentou contato com um candidato em risco, feito
pelo Console de Intervenção. `score_at_creation` congela o score do candidato
no momento do contato — é a base de comparação para a medição de impacto 7
dias depois (`measured_at`/`score_after`/`had_activity_after`), que fecha o
loop "o risco médio caiu X%" pedido pelo produto.

A medição roda como parte do mesmo job agendado que recalcula os scores (ver
`app.core.scheduler`): a cada tick, ele processa intervenções com
`created_at <= agora - 7 dias` e `measured_at IS NULL`.
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

InterventionChannel = Literal["call", "whatsapp", "other"]
InterventionOutcome = Literal["reached", "no_answer", "other"]

_VALID_CHANNELS: Final = ("call", "whatsapp", "other")
_VALID_OUTCOMES: Final = ("reached", "no_answer", "other")


class Intervention(Base):
    """Uma tentativa de contato registrada por um coordenador."""

    __tablename__ = "interventions"
    __table_args__ = (
        CheckConstraint(f"channel IN {_VALID_CHANNELS}", name="ck_intervention_channel"),
        CheckConstraint(f"outcome IN {_VALID_OUTCOMES}", name="ck_intervention_outcome"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # Coordenador/admin que registrou a intervenção.
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    channel: Mapped[InterventionChannel] = mapped_column(String(20), nullable=False)
    outcome: Mapped[InterventionOutcome] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Snapshot no momento do contato — base da medição de impacto.
    score_at_creation: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )

    # Preenchidos pelo job, ~7 dias depois (ver módulo docstring).
    measured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    had_activity_after: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Intervention candidate_profile_id={self.candidate_profile_id} "
            f"channel={self.channel} outcome={self.outcome}>"
        )
