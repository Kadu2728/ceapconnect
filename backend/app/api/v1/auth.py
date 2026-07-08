"""Router de autenticação (EPIC 02).

Cada endpoint apenas extrai as dependências (sessão de banco), delega a
regra de negócio para `app.services.auth_service` e monta o envelope
`ApiResponse`. Nenhuma lógica de negócio deve viver aqui.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
)
from app.schemas.response import ApiResponse
from app.schemas.user import UserSummary
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=ApiResponse[UserSummary],
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo candidato",
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserSummary]:
    """Cria uma nova conta de candidato.

    A conta nasce ativa (sem fluxo de confirmação por e-mail) e não retorna
    tokens — o candidato deve autenticar-se em seguida via `/auth/login`.
    """
    data = await auth_service.register_user(db, payload)
    return ApiResponse(success=True, message="Cadastro realizado com sucesso.", data=data)


@router.post(
    "/login",
    response_model=ApiResponse[TokenPairResponse],
    summary="Autenticar candidato",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenPairResponse]:
    """Autentica o candidato e retorna o par de tokens (access + refresh)."""
    data = await auth_service.authenticate_user(db, payload.email, payload.password)
    return ApiResponse(success=True, message="Login realizado com sucesso.", data=data)


@router.post(
    "/refresh",
    response_model=ApiResponse[AccessTokenResponse],
    summary="Renovar access token",
)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AccessTokenResponse]:
    """Emite um novo access token a partir de um refresh token válido."""
    access_token = await auth_service.refresh_access_token(db, payload.refresh_token)
    data = AccessTokenResponse(access_token=access_token)
    return ApiResponse(success=True, message="Token atualizado com sucesso.", data=data)
