"""Models SQLAlchemy de coorte (EPIC 14 — Predição de evasão, fase 1).

`Cohort` é a turma/processo seletivo a que um candidato pertence (ex.: "Processo
Seletivo 2026.1"). `CoordinatorCohort` liga um coordenador às coortes que ele
acompanha — é a base do **escopo do RBAC**: um coordenador só enxerga candidatos
das suas coortes; um admin enxerga todas.

O vínculo é N:N de propósito: um coordenador pode cuidar de mais de uma turma
(e uma turma pode ter mais de um coordenador).
"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Cohort(Base, TimestampMixin):
    """Turma/processo seletivo a que os candidatos pertencem."""

    __tablename__ = "cohorts"
    __table_args__ = (UniqueConstraint("year", "term", name="uq_cohort_year_term"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # "1" ou "2" (semestre). String em vez de int para admitir rótulos futuros
    # (ex.: "verao") sem migration.
    term: Mapped[str] = mapped_column(String(10), nullable=False)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Data única da formação obrigatória de pais/responsáveis desta coorte
    # (mentoria do CEAP: se o responsável não participa, o candidato perde a
    # vaga). Uma data por edital — não por candidato — porque toda a turma
    # compartilha a mesma sessão. Usada pelo sinal de risco do responsável em
    # `app.services.risk_feature_service`.
    guardian_training_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Cohort id={self.id} name={self.name!r}>"


class CoordinatorCohort(Base):
    """Vínculo coordenador ↔ coorte — define o escopo de acesso do coordenador.

    Não usa `TimestampMixin`: `created_at` já basta para uma entidade imutável
    (o vínculo é criado ou removido, nunca atualizado).
    """

    __tablename__ = "coordinator_cohorts"
    __table_args__ = (
        UniqueConstraint("user_id", "cohort_id", name="uq_coordinator_cohort_user_cohort"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    cohort_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("cohorts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<CoordinatorCohort user_id={self.user_id} cohort_id={self.cohort_id}>"
