"""Model SQLAlchemy da entidade `EventRegistration` (EPIC 03/07 — Eventos).

Junção candidato ↔ evento: registra a inscrição de um candidato em um
evento. O par (candidate_profile_id, event_id) é único — uma inscrição por
candidato por evento.

Não usa `TimestampMixin`: `registered_at` já cumpre o papel de "quando este
registro passou a existir" para uma entidade que nunca é atualizada.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EventRegistration(Base):
    """Inscrição de um candidato em um evento do catálogo."""

    __tablename__ = "event_registrations"
    __table_args__ = (
        UniqueConstraint(
            "candidate_profile_id", "event_id", name="uq_event_registration_profile_event"
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
    event_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<EventRegistration candidate_profile_id={self.candidate_profile_id} "
            f"event_id={self.event_id}>"
        )
