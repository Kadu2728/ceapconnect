"""Model SQLAlchemy da entidade `PushSubscription` (EPIC 18 — PWA + push).

Uma linha por dispositivo/navegador inscrito — um candidato pode ter várias
(celular + notebook, por exemplo). `endpoint` é único: reinscrever o mesmo
navegador atualiza as chaves em vez de duplicar.
"""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class PushSubscription(Base, TimestampMixin):
    """Inscrição de push de um dispositivo/navegador do candidato."""

    __tablename__ = "push_subscriptions"

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
    endpoint: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    p256dh: Mapped[str] = mapped_column(String(255), nullable=False)
    auth: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<PushSubscription id={self.id} candidate_profile_id={self.candidate_profile_id}>"
