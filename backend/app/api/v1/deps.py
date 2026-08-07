"""Dependencies reutilizáveis do FastAPI para a v1 da API.

Centraliza aqui (em vez de espalhar por routers) qualquer verificação que
precise ser injetada via `Depends` em múltiplas rotas: autenticação via Bearer
token e o controle de acesso por papel/coorte (RBAC — EPIC 14).

Os tipos e regras puras do RBAC (`CohortScope`, `is_admin`) vivem em
`app.core.rbac` — este módulo só adiciona a fiação de `Depends` em cima deles,
para que services possam depender do conceito de escopo sem depender da
camada HTTP.
"""

import hmac

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.rbac import CohortScope, is_admin
from app.models.user import ROLE_COORDINATOR, User
from app.repositories.cohort_repository import CohortRepository
from app.services import auth_service

__all__ = [
    "CohortScope",
    "get_cohort_scope",
    "get_current_admin",
    "get_current_coordinator",
    "get_current_user",
    "is_admin",
    "verify_internal_api_key",
]

_bearer_scheme = HTTPBearer(auto_error=False)
_INTERNAL_API_KEY_HEADER = "X-Internal-Api-Key"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve o usuário autenticado a partir do header `Authorization: Bearer`.

    Usar como `Depends(get_current_user)` em qualquer rota protegida.
    Levanta `UnauthorizedException` (401) se o header estiver ausente ou o
    token for inválido/expirado — nunca deixa a rota executar sem usuário
    resolvido.
    """
    if credentials is None:
        raise UnauthorizedException("Não autenticado.")

    return await auth_service.get_current_user(db, credentials.credentials)


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Garante que o usuário autenticado é administrador.

    Usar como `Depends(get_current_admin)` nas rotas do painel admin. Levanta
    `ForbiddenException` (403) para usuários autenticados sem privilégio.
    """
    if not is_admin(current_user):
        raise ForbiddenException("Acesso restrito a administradores.")
    return current_user


async def get_current_coordinator(current_user: User = Depends(get_current_user)) -> User:
    """Garante que o usuário é coordenador **ou** administrador.

    Usar nas rotas do console de intervenção: o coordenador enxerga apenas as
    próprias coortes (ver `CohortScope`), o admin enxerga todas.
    """
    if current_user.role != ROLE_COORDINATOR and not is_admin(current_user):
        raise ForbiddenException("Acesso restrito a coordenadores.")
    return current_user


async def get_cohort_scope(
    current_user: User = Depends(get_current_coordinator),
    db: AsyncSession = Depends(get_db),
) -> CohortScope:
    """Resolve o escopo de coortes do usuário autenticado (admin = irrestrito)."""
    if is_admin(current_user):
        return CohortScope(user=current_user, cohort_ids=None)

    cohort_ids = await CohortRepository(db).list_cohort_ids_for_coordinator(current_user.id)
    return CohortScope(user=current_user, cohort_ids=cohort_ids)


async def verify_internal_api_key(
    x_internal_api_key: str | None = Header(default=None, alias=_INTERNAL_API_KEY_HEADER),
) -> None:
    """Protege rotas internas (ex.: recompute de risco) por API key, não por JWT.

    Usar como `Depends(verify_internal_api_key)`. **Fail-closed**: se
    `INTERNAL_API_KEY` não estiver configurada no ambiente, o endpoint recusa
    toda chamada — nunca abre a rota "por acidente" num deploy sem a variável
    definida. Comparação em tempo constante (`hmac.compare_digest`) para não
    vazar a chave por timing attack.
    """
    configured_key = settings.internal_api_key
    if not configured_key:
        raise UnauthorizedException("Endpoint interno não configurado.")

    if not x_internal_api_key or not hmac.compare_digest(x_internal_api_key, configured_key):
        raise UnauthorizedException("Chave de API interna inválida.")
