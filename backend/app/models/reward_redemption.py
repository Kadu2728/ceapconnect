"""Model SQLAlchemy da entidade `RewardRedemption` (EPIC 13 — Recompensas).

Junção candidato ↔ recompensa: registra o **resgate** de uma recompensa e seu
ciclo de entrega. O par (candidate_profile_id, reward_id) é único — uma
recompensa só pode ser resgatada uma vez por candidato.

Ciclo do status:
- `pending`   → resgatada pelo candidato, aguardando a equipe entregar;
- `fulfilled` → entregue/confirmada pelo admin (painel);
- `cancelled` → resgate desfeito (reservado; sem fluxo de UI nesta fase).
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

RewardRedemptionStatus = Literal["pending", "fulfilled", "cancelled"]

STATUS_PENDING: Final = "pending"
STATUS_FULFILLED: Final = "fulfilled"
STATUS_CANCELLED: Final = "cancelled"

_VALID_STATUSES: Final = (STATUS_PENDING, STATUS_FULFILLED, STATUS_CANCELLED)


class RewardRedemption(Base):
    """Resgate de uma recompensa por um candidato, com seu status de entrega."""

    __tablename__ = "reward_redemptions"
    __table_args__ = (
        UniqueConstraint(
            "candidate_profile_id",
            "reward_id",
            name="uq_reward_redemption_profile_reward",
        ),
        CheckConstraint(
            f"status IN {_VALID_STATUSES}",
            name="ck_reward_redemption_status",
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
    reward_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("rewards.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[RewardRedemptionStatus] = mapped_column(
        String(20),
        default=STATUS_PENDING,
        server_default=STATUS_PENDING,
        index=True,
        nullable=False,
    )
    redeemed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    # Preenchido quando o admin confirma a entrega (status → fulfilled).
    fulfilled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<RewardRedemption candidate_profile_id={self.candidate_profile_id} "
            f"reward_id={self.reward_id} status={self.status}>"
        )
