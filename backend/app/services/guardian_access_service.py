"""Regra de negócio do RBAC do responsável (conta própria, autenticada).

Orquestra `GuardianScope` (resolvido em `deps.py`, nunca em memória aqui) +
os dados de jornada já existentes — nenhuma query nova de comportamento,
só uma composição read-only do que o Dashboard do candidato e o Perfil já
calculam. Fonte de risco (`RiskScoreRepository`/`risk_feature_service`)
nunca é importada neste módulo, de propósito: é a garantia estrutural de
que o responsável não pode ver o score, não só uma convenção de schema.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.rbac import GuardianScope
from app.models.candidate_document import REQUIRED_DOCUMENT_TYPES
from app.models.candidate_profile import CandidateProfile
from app.models.guardian_candidate_link import CONSENT_PENDING
from app.models.journey_step import JourneyStep
from app.models.user import User
from app.repositories.candidate_document_repository import CandidateDocumentRepository
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.cohort_repository import CohortRepository
from app.repositories.guardian_candidate_link_repository import GuardianCandidateLinkRepository
from app.repositories.guardian_repository import GuardianRepository
from app.repositories.journey_step_repository import JourneyStepRepository
from app.repositories.user_repository import UserRepository
from app.schemas.guardian_access import (
    GuardianChildItem,
    GuardianChildJourneyResponse,
    GuardianChildrenResponse,
)
from app.services import journey_service

_REQUIRED_DOCUMENT_COUNT = len(REQUIRED_DOCUMENT_TYPES)


async def list_children(db: AsyncSession, scope: GuardianScope) -> GuardianChildrenResponse:
    """Filhos vinculados e autorizados — nunca lê além de `scope.candidate_profile_ids`."""
    if not scope.candidate_profile_ids:
        return GuardianChildrenResponse(children=[])

    profiles = await CandidateProfileRepository(db).get_by_ids(scope.candidate_profile_ids)
    user_map = {
        user.id: user for user in await UserRepository(db).get_by_ids([p.user_id for p in profiles])
    }
    steps = await JourneyStepRepository(db).list_ordered()

    items = []
    for profile in profiles:
        user = user_map.get(profile.user_id)
        if user is None:
            continue
        items.append(_build_child_item(profile, user, steps))

    return GuardianChildrenResponse(children=items)


async def link_child(db: AsyncSession, guardian_user: User, token: str) -> GuardianChildItem:
    """Anexa mais um filho à conta já autenticada do responsável (link mágico).

    Distinto de `guardian_portal_service.activate_account` (que cria a
    conta): aqui a conta já existe, o link só serve para autorizar mais um
    candidato — o caso de dois irmãos no CEAP com o mesmo responsável.
    Idempotente: se o vínculo já existe, devolve o item existente em vez de
    tentar duplicar.
    """
    guardian = await GuardianRepository(db).get_by_confirmation_token(token)
    if guardian is None:
        raise NotFoundException("Link inválido ou expirado.")

    link_repo = GuardianCandidateLinkRepository(db)
    existing = await link_repo.get(
        guardian_user_id=guardian_user.id, candidate_profile_id=guardian.candidate_profile_id
    )
    if existing is None:
        await link_repo.create(
            guardian_user_id=guardian_user.id,
            candidate_profile_id=guardian.candidate_profile_id,
            consent_status=CONSENT_PENDING,
        )
        await db.commit()

    profile = await CandidateProfileRepository(db).get_by_id(guardian.candidate_profile_id)
    if profile is None:
        raise NotFoundException("Candidato não encontrado.")
    child_user = await UserRepository(db).get_by_id(profile.user_id)
    if child_user is None:
        raise NotFoundException("Candidato não encontrado.")

    steps = await JourneyStepRepository(db).list_ordered()
    return _build_child_item(profile, child_user, steps)


def _build_child_item(
    profile: CandidateProfile, user: User, steps: list[JourneyStep]
) -> GuardianChildItem:
    journey = journey_service.build_journey_progress(steps, profile.current_journey_step_key)
    current_step_label = next(
        (s.label for s in journey.steps if s.key == journey.current_step_key),
        journey.current_step_key,
    )
    return GuardianChildItem(
        candidate_profile_id=str(profile.id),
        name=user.name,
        current_step_label=current_step_label,
        journey_percentage=journey.percentage,
    )


async def get_child_journey(
    db: AsyncSession, scope: GuardianScope, candidate_profile_id: uuid.UUID
) -> GuardianChildJourneyResponse:
    """Jornada essencial de um filho — 403 se fora do escopo do responsável.

    A checagem de escopo acontece **antes** de qualquer leitura de dado do
    candidato: um `candidate_profile_id` fora de `scope.candidate_profile_ids`
    nunca chega a resolver nome, jornada ou qualquer outro campo.
    """
    if not scope.allows(candidate_profile_id):
        raise ForbiddenException("Você não tem acesso a este candidato.")

    profile = await CandidateProfileRepository(db).get_by_id(candidate_profile_id)
    if profile is None:
        raise NotFoundException("Candidato não encontrado.")

    user = await UserRepository(db).get_by_id(profile.user_id)
    if user is None:
        raise NotFoundException("Candidato não encontrado.")

    steps = await JourneyStepRepository(db).list_ordered()
    journey = journey_service.build_journey_progress(steps, profile.current_journey_step_key)

    doc_counts = await CandidateDocumentRepository(db).count_by_profile_ids([profile.id])
    pending_documents = max(0, _REQUIRED_DOCUMENT_COUNT - doc_counts.get(profile.id, 0))

    guardian_training_date = None
    if profile.cohort_id is not None:
        cohort = await CohortRepository(db).get_by_id(profile.cohort_id)
        guardian_training_date = cohort.guardian_training_date if cohort is not None else None

    contact_guardian = await GuardianRepository(db).get_primary_for_profile(profile.id)

    return GuardianChildJourneyResponse(
        candidate_name=user.name,
        journey=journey,
        pending_required_documents=pending_documents,
        exam_date=profile.exam_date,
        exam_location=settings.exam_location,
        interview_date=profile.interview_date,
        interview_location=settings.interview_location,
        guardian_training_date=guardian_training_date,
        guardian_training_confirmed=(
            contact_guardian is not None and contact_guardian.training_confirmed_at is not None
        ),
        guardian_training_attended=(
            contact_guardian is not None and contact_guardian.training_attended_at is not None
        ),
    )
