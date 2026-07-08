"""Model SQLAlchemy da entidade `MissionProgress` (EPIC 03/05 — Missões).

Junção candidato ↔ missão: representa o progresso individual de cada
candidato em cada missão do catálogo. Uma linha "pending" é criada
automaticamente para toda missão existente no momento do registro do
candidato (ver `app.services.candidate_profile_service`), garantindo que o
Dashboard sempre tenha uma "próxima missão" real para exibir.

O par (candidate_profile_id, mission_id) é único — nunca duplica progresso.

Status é modelado como `String` + `CHECK CONSTRAINT` (em vez de um Postgres
`ENUM` nativo) propositalmente: o conjunto de valores ainda pode evoluir
durante o EPIC 05 (ex.: "in_progress") e alterar um ENUM nativo do Postgres
exige uma migration `ALTER TYPE` mais custosa do que ajustar uma constraint.
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin

MissionProgressStatus = Literal["pending", "completed"]

STATUS_PENDING: Final = "pending"
STATUS_COMPLETED: Final = "completed"
_VALID_STATUSES: Final = (STATUS_PENDING, STATUS_COMPLETED)


class MissionProgress(Base, TimestampMixin):
    """Progresso de um candidato em uma missão específica do catálogo."""

    __tablename__ = "mission_progresses"
    __table_args__ = (
        UniqueConstraint(
            "candidate_profile_id", "mission_id", name="uq_mission_progress_profile_mission"
        ),
        CheckConstraint(
            f"status IN {_VALID_STATUSES}",
            name="ck_mission_progress_status",
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
        index=True,
        nullable=False,
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[MissionProgressStatus] = mapped_column(
        String(20),
        default=STATUS_PENDING,
        index=True,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<MissionProgress candidate_profile_id={self.candidate_profile_id} "
            f"mission_id={self.mission_id} status={self.status}>"
        )
