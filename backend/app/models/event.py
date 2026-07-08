"""Model SQLAlchemy da entidade `Event` (EPIC 03/07 — Eventos).

Catálogo global de eventos da comunidade CEAP. Populado via seed
(`app.core.seed`); CRUD administrativo é EPIC 10, fora de escopo.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Event(Base, TimestampMixin):
    """Evento da comunidade (ex.: palestra, simulado presencial)."""

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<Event id={self.id} title={self.title!r} date={self.date}>"
