"""Regra de negócio da jornada do responsável — alvo duplo do console + Área de Pais.

Reaproveita o mesmo `CohortScope` do Console de candidatos: um responsável só
é visível/acionável por quem tem acesso à coorte do candidato vinculado —
nenhuma peça nova de RBAC precisou ser criada.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.rbac import CohortScope
from app.models.candidate_profile import CandidateProfile
from app.models.guardian import Guardian
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.cohort_repository import CohortRepository
from app.repositories.guardian_intervention_repository import GuardianInterventionRepository
from app.repositories.guardian_repository import GuardianRepository
from app.repositories.user_repository import UserRepository
from app.schemas.guardian import (
    CohortTrainingDateUpdateRequest,
    GuardianAtRiskItem,
    GuardianInterventionCreateRequest,
    GuardianInterventionItem,
    GuardianMilestoneItem,
    GuardiansAtRiskResponse,
)
from app.services import achievement_service


async def get_at_risk(db: AsyncSession, scope: CohortScope) -> GuardiansAtRiskResponse:
    """Famílias que precisam de atenção: sem responsável cadastrado, ou
    responsável que ainda não concluiu a formação obrigatória.

    Quem já concluiu (`training_attended_at` preenchido) nunca aparece aqui —
    a lista é sempre "quem precisa de ação agora", não um roster completo.
    """
    profiles = await CandidateProfileRepository(db).list_active_candidates()
    if scope.cohort_ids is not None:
        allowed = set(scope.cohort_ids)
        profiles = [p for p in profiles if p.cohort_id in allowed]
    if not profiles:
        return GuardiansAtRiskResponse(items=[], total=0)

    guardian_map = await GuardianRepository(db).map_primary_by_profile_ids([p.id for p in profiles])
    user_map = {
        user.id: user for user in await UserRepository(db).get_by_ids([p.user_id for p in profiles])
    }
    cohorts_by_id = {cohort.id: cohort for cohort in await CohortRepository(db).list_all()}
    today = datetime.now(UTC).date()

    items: list[GuardianAtRiskItem] = []
    for profile in profiles:
        guardian = guardian_map.get(profile.id)
        if guardian is not None and guardian.training_attended_at is not None:
            continue

        user = user_map.get(profile.user_id)
        if user is None:
            continue

        cohort = cohorts_by_id.get(profile.cohort_id) if profile.cohort_id is not None else None
        training_date = cohort.guardian_training_date if cohort is not None else None
        reason = _resolve_reason(guardian, training_date, today)

        items.append(
            GuardianAtRiskItem(
                candidate_profile_id=profile.id,
                candidate_name=user.name,
                candidate_email=user.email,
                cohort_id=profile.cohort_id,
                cohort_name=cohort.name if cohort is not None else None,
                guardian_id=guardian.id if guardian is not None else None,
                guardian_name=guardian.name if guardian is not None else None,
                guardian_phone=guardian.phone if guardian is not None else None,
                guardian_email=guardian.email if guardian is not None else None,
                training_confirmed_at=(
                    guardian.training_confirmed_at if guardian is not None else None
                ),
                training_attended_at=None,
                guardian_training_date=training_date,
                reason=reason,
            )
        )

    # Sem responsável cadastrado primeiro (o caso mais urgente — nem dá pra
    # contatar ninguém ainda), depois em ordem alfabética do candidato.
    items.sort(key=lambda item: (item.guardian_id is not None, item.candidate_name))
    return GuardiansAtRiskResponse(items=items, total=len(items))


def _resolve_reason(guardian: Guardian | None, training_date, today) -> str:
    if guardian is None:
        return "Nenhum responsável cadastrado"
    if training_date is not None and today > training_date:
        return "Não compareceu à formação obrigatória (prazo vencido)"
    return "Ainda não confirmou presença na formação obrigatória"


async def create_intervention(
    db: AsyncSession, scope: CohortScope, payload: GuardianInterventionCreateRequest
) -> GuardianInterventionItem:
    """Registra um contato com o responsável."""
    guardian, _profile = await _get_guardian_in_scope(db, scope, payload.guardian_id)

    intervention = await GuardianInterventionRepository(db).create(
        guardian_id=guardian.id,
        created_by_user_id=scope.user.id,
        channel=payload.channel,
        outcome=payload.outcome,
        notes=payload.notes,
    )
    await db.commit()

    return GuardianInterventionItem(
        id=intervention.id,
        channel=intervention.channel,
        outcome=intervention.outcome,
        notes=intervention.notes,
        created_by_name=scope.user.name,
        created_at=intervention.created_at,
    )


async def mark_training_confirmed(
    db: AsyncSession, scope: CohortScope, guardian_id: uuid.UUID
) -> GuardianMilestoneItem:
    """Marca que o responsável confirmou presença — sinal leve, não zera o risco."""
    guardian, _profile = await _get_guardian_in_scope(db, scope, guardian_id)
    guardian.training_confirmed_at = datetime.now(UTC)
    await db.commit()
    return _to_milestone_item(guardian)


async def mark_training_attended(
    db: AsyncSession, scope: CohortScope, guardian_id: uuid.UUID
) -> GuardianMilestoneItem:
    """Marca presença de fato na formação — zera o risco e desbloqueia o marco
    simbólico "Responsável na Jornada" na tela do candidato (sem XP)."""
    guardian, profile = await _get_guardian_in_scope(db, scope, guardian_id)
    guardian.training_attended_at = datetime.now(UTC)
    await achievement_service.unlock_guardian_training(db, profile)
    await db.commit()
    return _to_milestone_item(guardian)


async def set_cohort_training_date(
    db: AsyncSession,
    scope: CohortScope,
    cohort_id: uuid.UUID,
    payload: CohortTrainingDateUpdateRequest,
) -> None:
    """Define/atualiza a data única da formação obrigatória de uma coorte."""
    if not scope.allows(cohort_id):
        raise ForbiddenException("Você não tem acesso a esta coorte.")
    cohort = await CohortRepository(db).get_by_id(cohort_id)
    if cohort is None:
        raise NotFoundException("Coorte não encontrada.")

    cohort.guardian_training_date = payload.guardian_training_date
    await db.commit()


async def _get_guardian_in_scope(
    db: AsyncSession, scope: CohortScope, guardian_id: uuid.UUID
) -> tuple[Guardian, CandidateProfile]:
    guardian = await GuardianRepository(db).get_by_id(guardian_id)
    if guardian is None:
        raise NotFoundException("Responsável não encontrado.")

    profile = await CandidateProfileRepository(db).get_by_id(guardian.candidate_profile_id)
    if profile is None:
        raise NotFoundException("Candidato vinculado não encontrado.")
    if not scope.allows(profile.cohort_id):
        raise ForbiddenException("Você não tem acesso a este responsável.")

    return guardian, profile


def _to_milestone_item(guardian: Guardian) -> GuardianMilestoneItem:
    return GuardianMilestoneItem(
        guardian_id=guardian.id,
        training_confirmed_at=guardian.training_confirmed_at,
        training_attended_at=guardian.training_attended_at,
    )
