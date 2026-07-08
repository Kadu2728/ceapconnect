"""Dependencies reutilizáveis do FastAPI para a v1 da API.

Centraliza aqui (em vez de espalhar por routers) qualquer verificação que
precise ser injetada via `Depends` em múltiplas rotas — a começar pela
autenticação via Bearer token.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from app.services import auth_service

_bearer_scheme = HTTPBearer(auto_error=False)


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
