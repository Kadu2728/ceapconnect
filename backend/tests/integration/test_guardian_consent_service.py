"""Teste de integração do consentimento do candidato (RBAC do responsável —
fase C).

Prova, contra um banco real, que só o próprio candidato decide o
`consent_status` do seu vínculo — nunca automático, nunca outro candidato.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.candidate_profile import CandidateProfile
from app.models.guardian_candidate_link import CONSENT_GRANTED, CONSENT_PENDING, CONSENT_REVOKED
from app.models.journey_step import JourneyStep
from app.models.user import User
from app.repositories.guardian_candidate_link_repository import GuardianCandidateLinkRepository
from app.repositories.user_repository import UserRepository
from app.services import guardian_consent_service


async def _link(
    db: AsyncSession, guardian: User, candidate_profile: CandidateProfile, *, status: str
) -> uuid.UUID:
    link = await GuardianCandidateLinkRepository(db).create(
        guardian_user_id=guardian.id,
        candidate_profile_id=candidate_profile.id,
        consent_status=status,
    )
    await db.flush()
    return link.id


async def _candidate_user(db: AsyncSession, candidate_profile: CandidateProfile) -> User:
    user = await UserRepository(db).get_by_id(candidate_profile.user_id)
    assert user is not None
    return user


async def test_listar_vinculos_traz_nome_e_email_do_responsavel(
    db_session: AsyncSession, guardian_user: User, candidate_profile: CandidateProfile
) -> None:
    await _link(db_session, guardian_user, candidate_profile, status=CONSENT_PENDING)
    candidate_user = await _candidate_user(db_session, candidate_profile)

    result = await guardian_consent_service.list_links(db_session, candidate_user)

    assert len(result.links) == 1
    assert result.links[0].guardian_name == guardian_user.name
    assert result.links[0].guardian_email == guardian_user.email
    assert result.links[0].consent_status == CONSENT_PENDING


async def test_autorizar_vinculo_muda_status_para_granted(
    db_session: AsyncSession, guardian_user: User, candidate_profile: CandidateProfile
) -> None:
    link_id = await _link(db_session, guardian_user, candidate_profile, status=CONSENT_PENDING)
    candidate_user = await _candidate_user(db_session, candidate_profile)

    item = await guardian_consent_service.grant_consent(db_session, candidate_user, link_id)

    assert item.consent_status == CONSENT_GRANTED
    authorized = await GuardianCandidateLinkRepository(db_session).list_authorized_candidate_ids(
        guardian_user.id
    )
    assert candidate_profile.id in authorized


async def test_revogar_vinculo_ja_autorizado_tira_do_escopo_do_responsavel(
    db_session: AsyncSession, guardian_user: User, candidate_profile: CandidateProfile
) -> None:
    link_id = await _link(db_session, guardian_user, candidate_profile, status=CONSENT_GRANTED)
    candidate_user = await _candidate_user(db_session, candidate_profile)

    item = await guardian_consent_service.revoke_consent(db_session, candidate_user, link_id)

    assert item.consent_status == CONSENT_REVOKED
    authorized = await GuardianCandidateLinkRepository(db_session).list_authorized_candidate_ids(
        guardian_user.id
    )
    assert candidate_profile.id not in authorized


async def test_candidato_nao_autoriza_vinculo_de_outro_candidato(
    db_session: AsyncSession,
    guardian_user: User,
    candidate_profile: CandidateProfile,
    journey_step: JourneyStep,
) -> None:
    """O teste central desta fase: um `link_id` real, mas de outro
    candidato, nunca pode ser autorizado/revogado — mesmo tratamento de um
    id inexistente (nunca revela que o vínculo existe)."""
    link_id = await _link(db_session, guardian_user, candidate_profile, status=CONSENT_PENDING)

    unique = uuid.uuid4().hex[:10]
    other_user = User(
        name="Outro Candidato",
        email=f"outro_{unique}@example.com",
        cpf=unique.ljust(11, "7")[:11],
        phone="11999990003",
        password_hash="not-a-real-hash",
    )
    db_session.add(other_user)
    await db_session.flush()
    other_profile = CandidateProfile(
        user_id=other_user.id, current_journey_step_key=journey_step.key
    )
    db_session.add(other_profile)
    await db_session.flush()

    with pytest.raises(NotFoundException):
        await guardian_consent_service.grant_consent(db_session, other_user, link_id)


async def test_vinculo_inexistente_levanta_not_found(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    candidate_user = await _candidate_user(db_session, candidate_profile)

    with pytest.raises(NotFoundException):
        await guardian_consent_service.grant_consent(db_session, candidate_user, uuid.uuid4())
