"""Schemas Pydantic relacionados à entidade `User` (EPIC 02).

Nunca incluir `password_hash` (ou qualquer dado sensível) em nenhum schema
de resposta — apenas os campos explicitamente previstos no contrato da API.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class UserSummary(BaseModel):
    """Representação pública mínima do usuário (cadastro, login)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    is_admin: bool
    # EPIC 14 — RBAC: o frontend usa isto (não `is_admin`) para decidir se
    # mostra a navegação do Console de Intervenção a um coordenador.
    role: UserRole


class UserMe(BaseModel):
    """Perfil completo do usuário autenticado (`GET /api/v1/users/me`)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    cpf: str
    phone: str
    created_at: datetime
