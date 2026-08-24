"""Fixtures compartilhadas dos testes (Candidate Journey OS — fase F1).

Duas categorias de teste, sem infraestrutura de banco emprestada de uma
para a outra:

- `tests/unit/`: funções puras (ex.: `risk_scoring.py`, futuramente
  `next_best_action_service.py`) — zero I/O, correm em qualquer máquina sem
  nenhuma configuração.
- `tests/integration/`: tocam o banco de verdade. Usam o padrão oficial do
  SQLAlchemy 2.0 para "external transaction" em testes — cada teste roda
  dentro de uma transação aberta pelo fixture, com `join_transaction_mode=
  "create_savepoint"`: quando o código sob teste chama `db.commit()` (como
  todo `service` deste projeto faz), o SQLAlchemy usa um SAVEPOINT em vez de
  fechar a transação de verdade. Ao final do teste, a transação externa
  sempre sofre rollback — nenhuma escrita de teste é persistida, mesmo
  contra um banco compartilhado (não há Postgres local disponível neste
  projeto fora do CI; ver DEPLOY.md/docker-compose.yml).

  Se `DATABASE_URL` não apontar para um banco alcançável (ex.: rodando fora
  do CI, sem rede até o Postgres), os testes de integração são pulados com
  um motivo explícito em vez de quebrar a suíte inteira — os testes
  unitários continuam rodando normalmente.
"""

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.database import engine
from app.models.candidate_profile import CandidateProfile
from app.models.journey_step import JourneyStep
from app.models.user import User

_DEFAULT_STEP_KEY = "inscricao"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Uma sessão por teste, presa a uma transação que nunca é commitada de fato."""
    try:
        connection = await engine.connect()
    except Exception as exc:  # noqa: BLE001 — motivo de skip, não falha de asserção
        pytest.skip(f"Banco de dados inalcançável ({settings.database_url!r}): {exc}")

    outer_transaction = await connection.begin()
    session_factory = async_sessionmaker(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    session = session_factory()

    try:
        yield session
    finally:
        await session.close()
        await outer_transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def journey_step(db_session: AsyncSession) -> JourneyStep:
    """A única etapa de catálogo necessária para criar um `CandidateProfile` válido."""
    step = JourneyStep(
        key=_DEFAULT_STEP_KEY,
        label="Inscrição",
        description="Etapa inicial da jornada.",
        order=1,
    )
    db_session.add(step)
    await db_session.flush()
    return step


@pytest_asyncio.fixture
async def candidate_profile(
    db_session: AsyncSession, journey_step: JourneyStep
) -> CandidateProfile:
    """Um candidato mínimo, válido, isolado por UUID único a cada execução."""
    unique = uuid.uuid4().hex[:10]
    user = User(
        name="Candidato de Teste",
        email=f"teste_{unique}@example.com",
        cpf=unique.ljust(11, "0")[:11],
        phone="11999990000",
        password_hash="not-a-real-hash",
    )
    db_session.add(user)
    await db_session.flush()

    profile = CandidateProfile(user_id=user.id, current_journey_step_key=journey_step.key)
    db_session.add(profile)
    await db_session.flush()
    return profile
