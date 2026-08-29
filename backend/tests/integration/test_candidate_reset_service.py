"""Teste de integração de `app.services.candidate_reset_service`.

Prova, contra um banco real, que o reset apaga o progresso antigo (não
apenas zera campos por cima dele) e recria um `CandidateProfile` do zero,
idêntico ao de um cadastro novo.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.candidate_profile import CandidateProfile
from app.models.journey_step import JourneyStep
from app.models.mission_progress import MissionProgress
from app.models.user import ROLE_GUARDIAN, User
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.mission_repository import MissionRepository
from app.services import candidate_reset_service


async def test_reset_apaga_progresso_antigo_e_recria_perfil_do_zero(
    db_session: AsyncSession, candidate_profile: CandidateProfile, journey_step: JourneyStep
) -> None:
    old_profile_id = candidate_profile.id
    candidate_profile.xp_total = 999
    candidate_profile.onboarded_at = None

    missions = await MissionRepository(db_session).list_all()
    assert missions, "banco de testes precisa de ao menos uma missão semeada"
    db_session.add(
        MissionProgress(candidate_profile_id=candidate_profile.id, mission_id=missions[0].id)
    )
    await db_session.flush()

    user = await db_session.get(User, candidate_profile.user_id)
    assert user is not None

    summary = await candidate_reset_service.reset_candidate_to_zero(db_session, user.email)

    assert summary.candidate_profile_id != str(old_profile_id)
    assert await CandidateProfileRepository(db_session).get_by_id(old_profile_id) is None

    fresh_profile = await CandidateProfileRepository(db_session).get_by_user_id(user.id)
    assert fresh_profile is not None
    assert str(fresh_profile.id) == summary.candidate_profile_id
    assert fresh_profile.xp_total == 0
    assert fresh_profile.onboarded_at is None
    assert fresh_profile.exam_date is not None
    assert fresh_profile.interview_date is not None


async def test_reset_de_email_inexistente_levanta_not_found(db_session: AsyncSession) -> None:
    with pytest.raises(NotFoundException):
        await candidate_reset_service.reset_candidate_to_zero(
            db_session, "ninguem-com-esse-email@example.com"
        )


async def test_reset_de_conta_que_nao_e_candidato_e_recusado(
    db_session: AsyncSession, guardian_user: User
) -> None:
    with pytest.raises(BadRequestException):
        await candidate_reset_service.reset_candidate_to_zero(db_session, guardian_user.email)


async def test_reset_remove_contas_de_responsavel_de_teste_indicadas(
    db_session: AsyncSession,
    candidate_profile: CandidateProfile,
    journey_step: JourneyStep,
    guardian_user: User,
) -> None:
    user = await db_session.get(User, candidate_profile.user_id)
    assert user is not None
    assert guardian_user.role == ROLE_GUARDIAN

    summary = await candidate_reset_service.reset_candidate_to_zero(
        db_session, user.email, also_remove_guardian_emails=[guardian_user.email]
    )

    assert summary.guardian_test_accounts_removed == 1
    assert await db_session.get(User, guardian_user.id) is None
