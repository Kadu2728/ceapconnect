"""Model SQLAlchemy da entidade `User` (EPIC 02 — Autenticação).

Representa os candidatos autenticáveis da plataforma. A conta nasce sempre
ativa (`is_active=True`) — não há, nesta fase, fluxo de confirmação por
e-mail antes da ativação (ver TODO em `app.services.auth_service`).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    """Candidato do processo seletivo, autenticável via e-mail e senha."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(11), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Acesso ao painel administrativo (EPIC 10). Promovido via
    # `python -m app.core.make_admin <email>`, nunca por endpoint público.
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Último login efetivo — base para a métrica "acessaram vs. não acessaram"
    # do painel admin. `None` = candidato que se cadastrou mas nunca entrou.
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
