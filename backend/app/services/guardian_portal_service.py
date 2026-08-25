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
from app.core.exceptions import NotFoundException
from app.models.guardian import Guardian
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.cohort_repository import CohortRepository
from app.repositories.guardian_repository import GuardianRepository
from app.repositories.user_repository import UserRepository
from app.schemas.guardian_portal import GuardianPortalView


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
    )


def _first_name(full_name: str) -> str:
    return full_name.strip().split(" ")[0] if full_name.strip() else full_name
