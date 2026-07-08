"""Model SQLAlchemy da entidade `CandidateAchievement` (EPIC 03/06 — Conquistas).

Junção candidato ↔ conquista: registra quando cada candidato desbloqueou
cada conquista. O par (candidate_profile_id, achievement_id) é único — uma
conquista só pode ser desbloqueada uma vez por candidato.

Não usa `TimestampMixin`: `unlocked_at` já cumpre o papel de "quando este
registro passou a existir" — duplicar com `created_at`/`updated_at` seria
redundante para uma entidade imutável (nunca é atualizada após criada).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CandidateAchievement(Base):
    """Registro de desbloqueio de uma conquista por um candidato."""

    __tablename__ = "candidate_achievements"
    __table_args__ = (
        UniqueConstraint(
            "candidate_profile_id",
            "achievement_id",
            name="uq_candidate_achievement_profile_achievement",
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
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<CandidateAchievement candidate_profile_id={self.candidate_profile_id} "
            f"achievement_id={self.achievement_id}>"
        )
