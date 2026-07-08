"""Model SQLAlchemy da entidade `Notification` (EPIC 03/08 — Notificações).

Notificação por candidato (nunca um catálogo global). Categoria é modelada
como `String` + `CHECK CONSTRAINT` pelo mesmo motivo de `MissionProgress`:
o conjunto de categorias ainda pode evoluir na EPIC 08.
"""

import uuid
from typing import Final, Literal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin

NotificationCategory = Literal["sistema", "eventos", "missoes", "lembretes", "resultado"]

_VALID_CATEGORIES: Final = ("sistema", "eventos", "missoes", "lembretes", "resultado")


class Notification(Base, TimestampMixin):
    """Notificação centralizada exibida na central de notificações do candidato."""

    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            f"category IN {_VALID_CATEGORIES}",
            name="ck_notification_category",
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
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[NotificationCategory] = mapped_column(String(20), index=True, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Notification id={self.id} category={self.category} read={self.read}>"
