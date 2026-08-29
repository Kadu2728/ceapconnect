"""Regra de negócio do Portal do Responsável (link mágico, sem conta/login).

Item 5 do backlog priorizado pelo usuário: até aqui, só o coordenador podia
marcar que o responsável confirmou presença na formação obrigatória
(`app.services.guardian_service.mark_training_confirmed`) — o próprio
responsável não tinha nenhum jeito de fazer isso. Este service resolve o
responsável pelo token do link mágico (nunca por login) e permite a
autoconfirmação.

Não usa `CohortScope` nem qualquer autenticação de usuário — a posse do
token é a única autorização, por isso o token precisa ser opaco e
imprevisível (`Guardian.confirmation_token`, gerado com `secrets.
token_urlsafe`).
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import hash_password
from app.models.guardian import Guardian
from app.models.guardian_candidate_link import CONSENT_PENDING
from app.models.user import ROLE_GUARDIAN
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.cohort_repository import CohortRepository
from app.repositories.guardian_candidate_link_repository import GuardianCandidateLinkRepository
from app.repositories.guardian_repository import GuardianRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPairResponse
from app.schemas.guardian_portal import GuardianAccountActivationRequest, GuardianPortalView
from app.services.auth_service import issue_token_pair


async def get_portal_view(db: AsyncSession, token: str) -> GuardianPortalView:
    """Resolve os dados exibidos na tela de confirmação a partir do token."""
    guardian = await _get_guardian_or_raise(db, token)
    return await _build_view(db, guardian)


async def confirm_training(db: AsyncSession, token: str) -> GuardianPortalView:
    """Autoconfirmação de presença — sinal leve, não zera o risco por si só
    (quem zera é `training_attended_at`, marcado pelo coordenador no dia).

    Idempotente: confirmar de novo (ou depois de já ter sido marcado
    presente) não sobrescreve nada, só devolve o estado atual.
    """
    guardian = await _get_guardian_or_raise(db, token)
    if guardian.training_confirmed_at is None:
        guardian.training_confirmed_at = datetime.now(UTC)
        await db.commit()
    return await _build_view(db, guardian)


async def activate_account(
    db: AsyncSession, token: str, payload: GuardianAccountActivationRequest
) -> TokenPairResponse:
    """Cria a conta de login do responsável a partir do link mágico.

    Cria SEMPRE uma conta nova — nunca reaproveita uma conta existente por
    e-mail/senha submetidos aqui (fluxo público, sem verificação de posse da
    conta antiga; reaproveitar seria uma porta de account takeover). Se o
    e-mail/CPF já pertence a qualquer conta, ou se este link já foi usado
    para ativar uma conta antes, a resposta é sempre 409 — o responsável que
    já tem conta deve fazer login normalmente, não ativar de novo.
    """
    guardian = await _get_guardian_or_raise(db, token)
    if guardian.activated_by_user_id is not None:
        raise ConflictException(
            "Este link já foi usado para criar uma conta. Faça login normalmente."
        )

    user_repo = UserRepository(db)
    if await user_repo.get_by_email(payload.email) is not None:
        raise ConflictException("Este e-mail já está cadastrado.")
    if await user_repo.get_by_cpf(payload.cpf) is not None:
        raise ConflictException("Este CPF já está cadastrado.")

    user = await user_repo.create(
        name=payload.name,
        email=payload.email,
        cpf=payload.cpf,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=ROLE_GUARDIAN,
    )

    await GuardianCandidateLinkRepository(db).create(
        guardian_user_id=user.id,
        candidate_profile_id=guardian.candidate_profile_id,
        consent_status=CONSENT_PENDING,
    )
    guardian.activated_by_user_id = user.id

    await db.commit()
    return issue_token_pair(user)


async def _get_guardian_or_raise(db: AsyncSession, token: str) -> Guardian:
    guardian = await GuardianRepository(db).get_by_confirmation_token(token)
    if guardian is None:
        raise NotFoundException("Link inválido ou expirado.")
    return guardian


async def _build_view(db: AsyncSession, guardian: Guardian) -> GuardianPortalView:
    profile = await CandidateProfileRepository(db).get_by_id(guardian.candidate_profile_id)
    if profile is None:
        raise NotFoundException("Link inválido ou expirado.")

    user = await UserRepository(db).get_by_id(profile.user_id)
    candidate_first_name = _first_name(user.name) if user is not None else "seu candidato"

    training_date = None
    if profile.cohort_id is not None:
        cohort = await CohortRepository(db).get_by_id(profile.cohort_id)
        training_date = cohort.guardian_training_date if cohort is not None else None

    return GuardianPortalView(
        candidate_first_name=candidate_first_name,
        training_date=training_date,
        training_location=settings.interview_location,
        training_confirmed_at=guardian.training_confirmed_at,
        training_attended_at=guardian.training_attended_at,
        account_already_active=guardian.activated_by_user_id is not None,
    )


def _first_name(full_name: str) -> str:
    return full_name.strip().split(" ")[0] if full_name.strip() else full_name
