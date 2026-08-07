"""Model SQLAlchemy da entidade `User` (EPIC 02 — Autenticação).

Representa os candidatos autenticáveis da plataforma. A conta nasce sempre
ativa (`is_active=True`) — não há, nesta fase, fluxo de confirmação por
e-mail antes da ativação (ver TODO em `app.services.auth_service`).
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import Boolean, CheckConstraint, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin

UserRole = Literal["candidate", "coordinator", "admin"]

ROLE_CANDIDATE: Final = "candidate"
ROLE_COORDINATOR: Final = "coordinator"
ROLE_ADMIN: Final = "admin"

_VALID_ROLES: Final = (ROLE_CANDIDATE, ROLE_COORDINATOR, ROLE_ADMIN)


class User(Base, TimestampMixin, SoftDeleteMixin):
    """Candidato do processo seletivo, autenticável via e-mail e senha."""

    __tablename__ = "users"
    __table_args__ = (CheckConstraint(f"role IN {_VALID_ROLES}", name="ck_user_role"),)

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
    #
    # Mantido por compatibilidade com o painel já existente. `role` é a fonte
    # de verdade a partir da EPIC 14 (RBAC com escopo); a checagem de admin
    # aceita ambos (`role == "admin" OR is_admin`) para migração sem ruptura.
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Papel do usuário (EPIC 14 — RBAC). `coordinator` enxerga apenas os
    # candidatos das coortes vinculadas em `coordinator_cohorts`; `admin`
    # enxerga todas. Nunca é exposto/alterado por endpoint público.
    role: Mapped[UserRole] = mapped_column(
        String(20),
        default=ROLE_CANDIDATE,
        server_default=ROLE_CANDIDATE,
        index=True,
        nullable=False,
    )
    # Último login efetivo — base para a métrica "acessaram vs. não acessaram"
    # do painel admin. `None` = candidato que se cadastrou mas nunca entrou.
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
