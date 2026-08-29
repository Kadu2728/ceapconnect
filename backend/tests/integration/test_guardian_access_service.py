"""Teste de integração do RBAC do responsável (`guardian_access_service`).

O teste central que o brief exige explicitamente: um responsável tentando
acessar um candidato ao qual não está vinculado deve falhar — sempre, mesmo
que o candidato exista de verdade no banco.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException
from app.core.rbac import GuardianScope
from app.models.candidate_profile import CandidateProfile
from app.models.guardian_candidate_link import CONSENT_GRANTED, CONSENT_PENDING
from app.models.user import User
from app.repositories.guardian_candidate_link_repository import GuardianCandidateLinkRepository
from app.services import guardian_access_service


async def _link(
    db: AsyncSession, guardian: User, candidate_profile: CandidateProfile, *, status: str
) -> None:
    await GuardianCandidateLinkRepository(db).create(
        guardian_user_id=guardian.id,
        candidate_profile_id=candidate_profile.id,
        consent_status=status,
    )
    await db.flush()


async def test_responsavel_nao_acessa_candidato_sem_vinculo(
    db_session: AsyncSession, guardian_user: User, candidate_profile: CandidateProfile
) -> None:
    """O teste que o brief pede explicitamente: sem NENHUM vínculo, acesso barrado."""
    empty_scope = GuardianScope(user=guardian_user, candidate_profile_ids=[])

    with pytest.raises(ForbiddenException):
        await guardian_access_service.get_child_journey(
            db_session, empty_scope, candidate_profile.id
        )


async def test_responsavel_acessa_candidato_vinculado_e_consentido(
    db_session: AsyncSession, guardian_user: User, candidate_profile: CandidateProfile
) -> None:
    await _link(db_session, guardian_user, candidate_profile, status=CONSENT_GRANTED)
    scope = GuardianScope(user=guardian_user, candidate_profile_ids=[candidate_profile.id])

    journey = await guardian_access_service.get_child_journey(
        db_session, scope, candidate_profile.id
    )

    assert journey.candidate_name == "Candidato de Teste"
    assert journey.journey.current_step_key == "inscricao"


async def test_vinculo_pending_nao_entra_no_escopo(
    db_session: AsyncSession, guardian_user: User, candidate_profile: CandidateProfile
) -> None:
    """`GuardianCandidateLinkRepository.list_authorized_candidate_ids` (usada por
    `get_guardian_scope`) nunca inclui vínculo `pending` — só testamos a query
    aqui, já que o `scope` em si é resolvido na dependency, não no service."""
    await _link(db_session, guardian_user, candidate_profile, status=CONSENT_PENDING)

    authorized = await GuardianCandidateLinkRepository(db_session).list_authorized_candidate_ids(
        guardian_user.id
    )

    assert authorized == []


async def test_resposta_da_jornada_nunca_tem_campo_de_risco(
    db_session: AsyncSession, guardian_user: User, candidate_profile: CandidateProfile
) -> None:
    """Checagem estrutural do freio de privacidade: o schema em si não tem
    nenhum campo de risco — não é uma convenção, é impossível vazar por acidente."""
    await _link(db_session, guardian_user, candidate_profile, status=CONSENT_GRANTED)
    scope = GuardianScope(user=guardian_user, candidate_profile_ids=[candidate_profile.id])

    journey = await guardian_access_service.get_child_journey(
        db_session, scope, candidate_profile.id
    )

    field_names = set(journey.model_fields.keys())
    forbidden_terms = {"risk", "risco", "score", "tier"}
    leaked = {f for f in field_names if any(term in f.lower() for term in forbidden_terms)}
    assert leaked == set()


async def test_listar_filhos_ignora_vinculo_nao_autorizado(
    db_session: AsyncSession, guardian_user: User, candidate_profile: CandidateProfile
) -> None:
    await _link(db_session, guardian_user, candidate_profile, status=CONSENT_PENDING)
    empty_scope = GuardianScope(user=guardian_user, candidate_profile_ids=[])

    result = await guardian_access_service.list_children(db_session, empty_scope)

    assert result.children == []
