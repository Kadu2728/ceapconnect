"""Model SQLAlchemy da entidade `Reward` (EPIC 13 — Recompensas).

Catálogo global de recompensas **reais** (cursos e certificações externas —
ex.: AWS Cloud Practitioner, Google) que o candidato desbloqueia por progressão.

Cada recompensa define **uma** condição de desbloqueio:
- `unlock_type="level"`     → exige atingir `required_level`;
- `unlock_type="achievement"` → exige desbloquear `required_achievement_id`.

Populado via seed (`app.core.seed`). A edição da lista final (o que o CEAP de
fato oferece) pode ser feita direto na tabela; `is_active=False` esconde uma
recompensa sem apagá-la. CRUD administrativo dedicado é evolução futura.
"""

import uuid
from typing import Final, Literal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin

RewardUnlockType = Literal["level", "achievement"]

_VALID_UNLOCK_TYPES: Final = ("level", "achievement")


class Reward(Base, TimestampMixin):
    """Recompensa do catálogo, com sua condição de desbloqueio."""

    __tablename__ = "rewards"
    __table_args__ = (
        CheckConstraint(
            f"unlock_type IN {_VALID_UNLOCK_TYPES}",
            name="ck_reward_unlock_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Instituição que oferece a recompensa (ex.: "Amazon Web Services").
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    # Rótulo curto de categoria (ex.: "Certificação", "Curso").
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    icon: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Nome do ícone lucide-react (ex.: 'award').",
    )

    unlock_type: Mapped[RewardUnlockType] = mapped_column(String(20), nullable=False)
    # Preenchido quando `unlock_type == "level"`.
    required_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Preenchido quando `unlock_type == "achievement"`. SET NULL: remover uma
    # conquista não apaga a recompensa (ela só fica sem gatilho até reconfigurar).
    required_achievement_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Destaque na vitrine (herói/ordenação prioritária).
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Soft-hide: recompensa fora do ar sem apagar histórico de resgates.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    # Ordem manual de exibição (menor primeiro; empate resolvido por created_at).
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Reward id={self.id} title={self.title!r}>"
