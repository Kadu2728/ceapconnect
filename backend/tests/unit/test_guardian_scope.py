"""Testes de `app.core.rbac.GuardianScope`. Sem I/O, sem banco."""

import uuid

from app.core.rbac import GuardianScope
from app.models.user import ROLE_GUARDIAN, User


def _fake_user() -> User:
    return User(
        id=uuid.uuid4(),
        name="Responsável",
        email="r@example.com",
        cpf="12345678901",
        phone="11999999999",
        password_hash="hash",
        role=ROLE_GUARDIAN,
    )


def test_permite_candidato_dentro_do_escopo() -> None:
    candidate_id = uuid.uuid4()
    scope = GuardianScope(user=_fake_user(), candidate_profile_ids=[candidate_id])
    assert scope.allows(candidate_id) is True


def test_nega_candidato_fora_do_escopo() -> None:
    scope = GuardianScope(user=_fake_user(), candidate_profile_ids=[uuid.uuid4()])
    assert scope.allows(uuid.uuid4()) is False


def test_escopo_vazio_nega_qualquer_candidato() -> None:
    """Nunca "vê tudo por omissão" — lista vazia é o padrão mais seguro."""
    scope = GuardianScope(user=_fake_user(), candidate_profile_ids=[])
    assert scope.allows(uuid.uuid4()) is False
