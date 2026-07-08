"""Mixins reutilizáveis para os models SQLAlchemy do projeto.

Centraliza os campos que se repetem em praticamente toda entidade do
domínio (`created_at`/`updated_at`, soft delete), conforme padrão definido
em DATABASE.md, evitando duplicação à medida que novos models (Journey,
Mission, Event etc.) forem criados nas próximas EPICs.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Adiciona `created_at`/`updated_at` gerenciados automaticamente pelo banco."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Adiciona suporte a soft delete via `deleted_at` (nulo = registro ativo)."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        """Indica se o registro foi (soft) deletado."""
        return self.deleted_at is not None
