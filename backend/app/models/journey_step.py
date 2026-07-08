"""Model SQLAlchemy da entidade `JourneyStep` (EPIC 03/04 — Dashboard/Jornada).

Catálogo fixo e global das etapas da jornada do candidato (não é por
candidato — é referenciado por `CandidateProfile.current_journey_step_key`).
Populado via seed (`app.core.seed`), nunca via CRUD administrativo nesta
fase (fora de escopo, ver EPIC 10).
"""

import uuid

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class JourneyStep(Base, TimestampMixin):
    """Etapa fixa do catálogo da jornada (ex.: "inscricao", "documentacao")."""

    __tablename__ = "journey_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    key: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)

    def __repr__(self) -> str:
        return f"<JourneyStep key={self.key} order={self.order}>"
