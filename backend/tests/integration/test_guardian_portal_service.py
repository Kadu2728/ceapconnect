"""Teste de integração de `app.services.guardian_portal_service` (item 5 do backlog).

Prova, contra um banco real, que o link mágico do responsável resolve os
dados certos e que a autoconfirmação é idempotente — chamar duas vezes não
sobrescreve o timestamp da primeira confirmação.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.candidate_profile import CandidateProfile
from app.models.guardian import Guardian
from app.models.user import ROLE_GUARDIAN
from app.repositories.guardian_candidate_link_repository import GuardianCandidateLinkRepository
from app.repositories.user_repository import UserRepository
from app.schemas.guardian_portal import GuardianAccountActivationRequest
from app.services import guardian_portal_service
from app.utils.validators import _calculate_cpf_check_digit


def _valid_cpf(seed: str) -> str:
    """Gera um CPF com dígitos verificadores reais a partir de um `seed`
    hexadecimal (ex.: `uuid4().hex`) — necessário porque
    `GuardianAccountActivationRequest` valida o CPF de verdade
    (`is_valid_cpf`), diferente das fixtures de `User` criadas direto via ORM
    (que não passam pela validação do schema). Aceita letras hex (a-f) do
    `uuid4().hex`, por isso `int(char, 16) % 10` em vez de `int(char)`."""
    base = [int(char, 16) % 10 for char in seed.ljust(9, "1")[:9]]
    if len(set(base)) == 1:
        base[-1] = (base[-1] + 1) % 10
    first = _calculate_cpf_check_digit(base)
    second = _calculate_cpf_check_digit(base + [first])
    return "".join(str(d) for d in [*base, first, second])


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


def _activation_payload(*, email: str, cpf: str) -> GuardianAccountActivationRequest:
    return GuardianAccountActivationRequest(
        name="Responsável de Teste",
        email=email,
        cpf=cpf,
        phone="11988887777",
        password="SenhaForte123",
        password_confirmation="SenhaForte123",
    )


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


async def test_ativar_conta_cria_usuario_responsavel_e_vinculo(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    guardian = await _create_guardian(db_session, candidate_profile)
    unique = uuid.uuid4().hex[:10]
    payload = _activation_payload(email=f"resp_{unique}@example.com", cpf=_valid_cpf(unique))

    tokens = await guardian_portal_service.activate_account(
        db_session, guardian.confirmation_token, payload
    )

    assert tokens.user.email == payload.email
    assert tokens.access_token
    assert tokens.refresh_token

    created_user = await UserRepository(db_session).get_by_email(payload.email)
    assert created_user is not None
    assert created_user.role == ROLE_GUARDIAN

    authorized = await GuardianCandidateLinkRepository(db_session).list_authorized_candidate_ids(
        created_user.id
    )
    assert candidate_profile.id in authorized

    view = await guardian_portal_service.get_portal_view(db_session, guardian.confirmation_token)
    assert view.account_already_active is True


async def test_ativar_conta_pelo_mesmo_link_duas_vezes_e_bloqueada(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    guardian = await _create_guardian(db_session, candidate_profile)
    unique = uuid.uuid4().hex[:10]

    await guardian_portal_service.activate_account(
        db_session,
        guardian.confirmation_token,
        _activation_payload(email=f"resp_{unique}@example.com", cpf=_valid_cpf(unique)),
    )

    with pytest.raises(ConflictException):
        await guardian_portal_service.activate_account(
            db_session,
            guardian.confirmation_token,
            _activation_payload(email=f"resp2_{unique}@example.com", cpf=_valid_cpf(unique[::-1])),
        )


async def test_ativar_conta_com_email_ja_cadastrado_e_bloqueada(
    db_session: AsyncSession, candidate_profile: CandidateProfile, guardian_user
) -> None:
    guardian = await _create_guardian(db_session, candidate_profile)

    with pytest.raises(ConflictException):
        await guardian_portal_service.activate_account(
            db_session,
            guardian.confirmation_token,
            _activation_payload(email=guardian_user.email, cpf=_valid_cpf(uuid.uuid4().hex)),
        )
