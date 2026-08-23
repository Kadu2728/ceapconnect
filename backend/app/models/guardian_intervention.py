"""Model SQLAlchemy da entidade `GuardianIntervention` (alvo duplo do console).

Espelha `app.models.intervention.Intervention`, mas para o responsável — o
console de intervenção não trata mais só o candidato como alvo (mentoria do
CEAP: o responsável é fator de evasão de primeira ordem).

Deliberadamente mais simples que `Intervention`: não há `score_at_creation`/
medição automática de impacto 7 dias depois — o outcome real de uma família
é a própria marcação de presença na formação (`Guardian.training_attended_at`,
ver `app.services.guardian_service.mark_training_attended`), não um score
que precisa de um job pra comparar antes/depois.
"""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.intervention import InterventionChannel, InterventionOutcome

_VALID_CHANNELS = ("call", "whatsapp", "other")
_VALID_OUTCOMES = ("reached", "no_answer", "other")


class GuardianIntervention(Base):
    """Uma tentativa de contato com o responsável, registrada por um coordenador."""

    __tablename__ = "guardian_interventions"
    __table_args__ = (
        CheckConstraint(f"channel IN {_VALID_CHANNELS}", name="ck_guardian_intervention_channel"),
        CheckConstraint(f"outcome IN {_VALID_OUTCOMES}", name="ck_guardian_intervention_outcome"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    guardian_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("guardians.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    channel: Mapped[InterventionChannel] = mapped_column(String(20), nullable=False)
    outcome: Mapped[InterventionOutcome] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<GuardianIntervention guardian_id={self.guardian_id} "
            f"channel={self.channel} outcome={self.outcome}>"
        )
