"""Model SQLAlchemy da entidade `Mission` (EPIC 03/05 — Dashboard/Missões).

Catálogo global de missões disponíveis para todos os candidatos. Populado
via seed (`app.core.seed`); CRUD administrativo é EPIC 10, fora de escopo.
"""

import uuid
from datetime import date

from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Mission(Base, TimestampMixin):
    """Missão do catálogo (ex.: "Conheça o CEAP"), com recompensa em XP."""

    __tablename__ = "missions"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"<Mission id={self.id} title={self.title!r}>"
