"""Regra de negócio de autenticação (EPIC 02).

Orquestra hashing de senha, emissão/validação de JWT e acesso a dados via
`UserRepository`. Roteadores (`app/api/v1/auth.py`, `app/api/v1/deps.py`)
apenas chamam estas funções — nenhuma regra de negócio deve viver neles.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.activity_event import EVENT_LOGIN
from app.models.user import User
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, TokenPairResponse
from app.schemas.user import UserSummary
from app.services import activity_event_service
from app.services.candidate_profile_service import bootstrap_new_candidate

_INVALID_CREDENTIALS_MESSAGE = "E-mail ou senha inválidos."
_INVALID_SESSION_MESSAGE = "Sessão inválida ou expirada."
_INVALID_REFRESH_MESSAGE = "Token de atualização inválido ou expirado."


async def register_user(db: AsyncSession, payload: RegisterRequest) -> UserSummary:
    """Cria um novo candidato. A conta nasce ativa, sem confirmação de e-mail.

    Também inicializa o perfil de gamificação (EPIC 03): `CandidateProfile`
    (já na 2ª etapa da jornada, já que o cadastro conclui a "Inscrição") e o
    progresso `pending` de cada missão do catálogo. Tudo em uma única
    transação — se qualquer etapa falhar, nada é persistido.

    TODO(futuro): introduzir fluxo de confirmação de e-mail antes da conta
    ser ativada. Desabilitado propositalmente nesta EPIC — decisão explícita
    do produto para permitir teste imediato do fluxo de autenticação.
    """
    repo = UserRepository(db)

    if await repo.get_by_email(payload.email) is not None:
        raise ConflictException("Este e-mail já está cadastrado.")
    if await repo.get_by_cpf(payload.cpf) is not None:
        raise ConflictException("Este CPF já está cadastrado.")

    user = await repo.create(
        name=payload.name,
        email=payload.email,
        cpf=payload.cpf,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
    )
    await bootstrap_new_candidate(db, user.id)

    await db.commit()
    await db.refresh(user)
    return UserSummary.model_validate(user)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> TokenPairResponse:
    """Autentica um candidato e emite o par de tokens (access + refresh).

    Nunca revela se foi o e-mail ou a senha que estava incorreta — a
    resposta de erro é sempre a mesma mensagem genérica.
    """
    repo = UserRepository(db)
    user = await repo.get_by_email(email)

    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise UnauthorizedException(_INVALID_CREDENTIALS_MESSAGE)

    # Registra o acesso: base da métrica "acessaram vs. não acessaram" (admin).
    user.last_login_at = datetime.now(UTC)

    # Tracking comportamental (EPIC 14): o login é o sinal mais forte de
    # atividade — alimenta a feature "dias desde a última atividade". Entra na
    # mesma transação do `last_login_at`.
    profile = await CandidateProfileRepository(db).get_by_user_id(user.id)
    if profile is not None:
        await activity_event_service.track(db, candidate_profile_id=profile.id, name=EVENT_LOGIN)

    await db.commit()

    return issue_token_pair(user)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
    """Emite um novo access token a partir de um refresh token válido."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise UnauthorizedException(_INVALID_REFRESH_MESSAGE)

    user = await _resolve_active_user(
        db, payload.get("sub"), error_message=_INVALID_REFRESH_MESSAGE
    )
    return create_access_token(str(user.id))


async def get_current_user(db: AsyncSession, access_token: str) -> User:
    """Resolve o usuário autenticado a partir de um access token válido.

    Consumida pela dependency `get_current_user` (`app/api/v1/deps.py`)
    usada para proteger rotas.
    """
    payload = decode_token(access_token)
    if payload is None or payload.get("type") != "access":
        raise UnauthorizedException(_INVALID_SESSION_MESSAGE)

    return await _resolve_active_user(
        db, payload.get("sub"), error_message=_INVALID_SESSION_MESSAGE
    )


def issue_token_pair(user: User) -> TokenPairResponse:
    """Monta o par de tokens JWT (access + refresh) para o usuário informado."""
    return TokenPairResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        user=UserSummary.model_validate(user),
    )


async def _resolve_active_user(
    db: AsyncSession, subject: str | None, *, error_message: str
) -> User:
    """Resolve o usuário ativo a partir do claim `sub` de um JWT já decodificado."""
    if not subject:
        raise UnauthorizedException(error_message)

    try:
        user_id = uuid.UUID(subject)
    except ValueError as exc:
        raise UnauthorizedException(error_message) from exc

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedException(error_message)

    return user
