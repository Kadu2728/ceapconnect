"""Model SQLAlchemy da entidade `CandidateProfile` (EPIC 03 — Dashboard).

Extensão 1:1 de `User` com os dados de gamificação/jornada do candidato.
Criado automaticamente no registro (`app.services.candidate_profile_service`),
nunca via endpoint dedicado nesta fase.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

# Step inicial usado apenas como default de schema (safety net). Na prática,
# o valor real é sempre atribuído explicitamente no registro do candidato por
# `candidate_profile_service.bootstrap_new_candidate`.
_DEFAULT_JOURNEY_STEP_KEY = "inscricao"


class CandidateProfile(Base, TimestampMixin, SoftDeleteMixin):
    """Perfil de gamificação/jornada do candidato, 1:1 com `User`."""

    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    xp_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    current_journey_step_key: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("journey_steps.key"),
        default=_DEFAULT_JOURNEY_STEP_KEY,
        nullable=False,
    )
    # Quando o candidato concluiu a tela de boas-vindas (onboarding do primeiro
    # login, USER_FLOW.md). `None` = ainda não viu — mostrar o onboarding.
    onboarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<CandidateProfile id={self.id} user_id={self.user_id}>"
