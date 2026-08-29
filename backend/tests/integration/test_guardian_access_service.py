"""Teste de integração do RBAC do responsável (`guardian_access_service`).

O teste central que o brief exige explicitamente: um responsável tentando
acessar um candidato ao qual não está vinculado deve falhar — sempre, mesmo
que o candidato exista de verdade no banco.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.rbac import GuardianScope
from app.models.candidate_profile import CandidateProfile
from app.models.guardian import Guardian
from app.models.guardian_candidate_link import CONSENT_GRANTED, CONSENT_PENDING
from app.models.journey_step import JourneyStep
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


async def _second_child_with_magic_link(db: AsyncSession, journey_step: JourneyStep) -> Guardian:
    """Um segundo candidato (ex.: irmão) com seu próprio contato `Guardian`
    (link mágico) — usado para testar `link_child` (anexar mais um filho a
    uma conta de responsável já existente)."""
    unique = uuid.uuid4().hex[:10]
    user = User(
        name="Segundo Filho de Teste",
        email=f"filho2_{unique}@example.com",
        cpf=unique.ljust(11, "6")[:11],
        phone="11999990002",
        password_hash="not-a-real-hash",
    )
    db.add(user)
    await db.flush()

    profile = CandidateProfile(user_id=user.id, current_journey_step_key=journey_step.key)
    db.add(profile)
    await db.flush()

    guardian = Guardian(candidate_profile_id=profile.id, is_primary=True)
    db.add(guardian)
    await db.flush()
    return guardian


async def test_link_child_anexa_um_segundo_filho_pelo_link(
    db_session: AsyncSession, guardian_user: User, journey_step: JourneyStep
) -> None:
    second_child_guardian = await _second_child_with_magic_link(db_session, journey_step)

    item = await guardian_access_service.link_child(
        db_session, guardian_user, second_child_guardian.confirmation_token
    )

    assert item.candidate_profile_id == str(second_child_guardian.candidate_profile_id)
    authorized = await GuardianCandidateLinkRepository(db_session).list_authorized_candidate_ids(
        guardian_user.id
    )
    assert second_child_guardian.candidate_profile_id in authorized


async def test_link_child_e_idempotente(
    db_session: AsyncSession, guardian_user: User, journey_step: JourneyStep
) -> None:
    second_child_guardian = await _second_child_with_magic_link(db_session, journey_step)

    await guardian_access_service.link_child(
        db_session, guardian_user, second_child_guardian.confirmation_token
    )
    # Chamar de novo com o mesmo link não deve levantar (UniqueConstraint) nem duplicar.
    await guardian_access_service.link_child(
        db_session, guardian_user, second_child_guardian.confirmation_token
    )

    links = await GuardianCandidateLinkRepository(db_session).list_for_guardian(guardian_user.id)
    matching = [
        link
        for link in links
        if link.candidate_profile_id == second_child_guardian.candidate_profile_id
    ]
    assert len(matching) == 1


async def test_link_child_com_token_invalido_levanta_not_found(
    db_session: AsyncSession, guardian_user: User
) -> None:
    with pytest.raises(NotFoundException):
        await guardian_access_service.link_child(db_session, guardian_user, "token-invalido")
