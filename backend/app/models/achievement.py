"""Model SQLAlchemy da entidade `Achievement` (EPIC 03/06 — Conquistas).

Catálogo global de conquistas desbloqueáveis. Populado via seed
(`app.core.seed`); CRUD administrativo é EPIC 10, fora de escopo.
"""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Achievement(Base, TimestampMixin):
    """Conquista do catálogo (ex.: "Primeira Missão"), com ícone lucide-react."""

    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Nome do ícone lucide-react (ex.: 'trophy').",
    )

    def __repr__(self) -> str:
        return f"<Achievement id={self.id} name={self.name!r}>"
