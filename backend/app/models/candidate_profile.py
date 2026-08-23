"""Model SQLAlchemy da entidade `CandidateProfile` (EPIC 03 — Dashboard).

Extensão 1:1 de `User` com os dados de gamificação/jornada do candidato.
Criado automaticamente no registro (`app.services.candidate_profile_service`),
nunca via endpoint dedicado nesta fase.
"""

import uuid
from datetime import date, datetime
from typing import Final, Literal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

# Step inicial usado apenas como default de schema (safety net). Na prática,
# o valor real é sempre atribuído explicitamente no registro do candidato por
# `candidate_profile_service.bootstrap_new_candidate`.
_DEFAULT_JOURNEY_STEP_KEY = "inscricao"

CandidateStatus = Literal["active", "approved", "evaded", "withdrawn"]

STATUS_ACTIVE: Final = "active"
STATUS_APPROVED: Final = "approved"
STATUS_EVADED: Final = "evaded"
STATUS_WITHDRAWN: Final = "withdrawn"

_VALID_STATUSES: Final = (STATUS_ACTIVE, STATUS_APPROVED, STATUS_EVADED, STATUS_WITHDRAWN)


class CandidateProfile(Base, TimestampMixin, SoftDeleteMixin):
    """Perfil de gamificação/jornada do candidato, 1:1 com `User`."""

    __tablename__ = "candidate_profiles"
    __table_args__ = (
        CheckConstraint(f"status IN {_VALID_STATUSES}", name="ck_candidate_profile_status"),
    )

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
    # Coorte (turma) do candidato (EPIC 14). Nulo = ainda não atribuído — o
    # coordenador só enxerga candidatos das suas coortes, então um candidato
    # sem coorte aparece apenas para admins. SET NULL: apagar a coorte não
    # apaga o candidato.
    cohort_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("cohorts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    current_journey_step_key: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("journey_steps.key"),
        default=_DEFAULT_JOURNEY_STEP_KEY,
        nullable=False,
    )
    # Quando o candidato concluiu a tela de boas-vindas (onboarding do primeiro
    # login, USER_FLOW.md). `None` = ainda não viu — mostrar o onboarding.
    onboarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Entrevista com o responsável (3ª etapa do processo seletivo real, EPIC 17).
    # Calculada automaticamente no bootstrap a partir de `exam_date`, mesmo
    # racional provisório de `default_exam_offset_days` — até o produto ter uma
    # data real configurável por edital.
    interview_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Contato e jornada do responsável: ver `app.models.guardian.Guardian`
    # (1 candidato pode ter mais de um responsável — não cabe mais em colunas
    # planas aqui; migrado de EPIC 17 na migration que criou `guardians`).
    # Outcome real do processo seletivo (rótulo usado no backtest do modelo de
    # risco — EPIC 14, fase 2). Mudança sempre manual, feita pelo coordenador
    # no Console de Intervenção: inferir automaticamente contaminaria o
    # rótulo com um critério ruidoso (ex.: inatividade não é o mesmo que
    # evasão confirmada).
    status: Mapped[CandidateStatus] = mapped_column(
        String(20), default=STATUS_ACTIVE, server_default=STATUS_ACTIVE, nullable=False
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<CandidateProfile id={self.id} user_id={self.user_id}>"
