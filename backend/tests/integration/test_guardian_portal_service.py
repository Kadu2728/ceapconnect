"""Teste de integração de `app.services.guardian_portal_service` (item 5 do backlog).

Prova, contra um banco real, que o link mágico do responsável resolve os
dados certos e que a autoconfirmação é idempotente — chamar duas vezes não
sobrescreve o timestamp da primeira confirmação.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.candidate_profile import CandidateProfile
from app.models.guardian import Guardian
from app.services import guardian_portal_service


async def _create_guardian(db: AsyncSession, candidate_profile: CandidateProfile) -> Guardian:
    guardian = Guardian(
        candidate_profile_id=candidate_profile.id,
        name="Responsável de Teste",
        phone="11988887777",
        email="responsavel@example.com",
        is_primary=True,
    )
    db.add(guardian)
    await db.flush()
    return guardian


async def test_portal_view_traz_primeiro_nome_do_candidato(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    guardian = await _create_guardian(db_session, candidate_profile)

    view = await guardian_portal_service.get_portal_view(db_session, guardian.confirmation_token)

    assert view.candidate_first_name == "Candidato"
    assert view.training_confirmed_at is None
    assert view.training_attended_at is None


async def test_confirmar_presenca_e_idempotente(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    guardian = await _create_guardian(db_session, candidate_profile)

    first = await guardian_portal_service.confirm_training(db_session, guardian.confirmation_token)
    assert first.training_confirmed_at is not None

    second = await guardian_portal_service.confirm_training(db_session, guardian.confirmation_token)
    assert second.training_confirmed_at == first.training_confirmed_at


async def test_token_invalido_levanta_not_found(db_session: AsyncSession) -> None:
    with pytest.raises(NotFoundException):
        await guardian_portal_service.get_portal_view(db_session, "token-que-nao-existe")


async def test_cada_responsavel_tem_um_token_unico_gerado_automaticamente(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    guardian = await _create_guardian(db_session, candidate_profile)

    assert guardian.confirmation_token
    assert len(guardian.confirmation_token) >= 32
