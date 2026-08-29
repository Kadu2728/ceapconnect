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
  unitários continuam rodando normalmente. A checagem de alcançabilidade
  roda **uma vez por sessão de teste** (`_database_reachable`, com timeout
  curto), não uma vez por teste — sem isso, cada teste de integração pagaria
  de novo o timeout de conexão (dezenas de segundos por tentativa em redes
  sem rota até o banco), tornando a suíte inteira lenta demais para rodar
  localmente à medida que mais testes de integração são adicionados.
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.database import engine
from app.models.candidate_profile import CandidateProfile
from app.models.journey_step import JourneyStep
from app.models.user import ROLE_GUARDIAN, User

_DEFAULT_STEP_KEY = "inscricao"
# Timeout curto de propósito: só precisa bastar para um Postgres de verdade
# responder (CI, ou um Postgres local) — uma rede sem rota até o host (este
# sandbox de desenvolvimento, ver DEPLOY.md) deve falhar rápido, não pendurar
# a suíte inteira no timeout default do SO (dezenas de segundos).
_DB_REACHABILITY_TIMEOUT_SECONDS = 5.0


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def _database_reachable() -> bool:
    """Só paga o custo do timeout de conexão uma vez por sessão inteira de testes."""
    try:
        connection = await asyncio.wait_for(
            engine.connect(), timeout=_DB_REACHABILITY_TIMEOUT_SECONDS
        )
    except Exception:  # noqa: BLE001 — motivo de skip, não falha de asserção
        return False
    await connection.close()
    return True


@pytest_asyncio.fixture
async def db_session(_database_reachable: bool) -> AsyncGenerator[AsyncSession]:
    """Uma sessão por teste, presa a uma transação que nunca é commitada de fato."""
    if not _database_reachable:
        pytest.skip(f"Banco de dados inalcançável ({settings.database_url!r}).")

    # `_database_reachable` só prova que uma conexão *anterior* funcionou —
    # em redes instáveis (ex.: handshake SSL que falha depois do connect
    # inicial, observado neste ambiente Windows/asyncpg), esta segunda
    # tentativa pode falhar mesmo com o probe tendo passado. Mesmo
    # tratamento: motivo de skip, nunca um ERROR de suíte.
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
    """A única etapa de catálogo necessária para criar um `CandidateProfile` válido.

    Idempotente: contra um banco já semeado (o Neon compartilhado de
    dev/produção — CI usa um Postgres efêmero e vazio), `key="inscricao"`
    já existe de verdade. Reaproveita a linha existente em vez de tentar
    inserir de novo (`UniqueViolationError`) — o catálogo de etapas é o
    mesmo em qualquer banco, não há motivo para o teste ter a sua própria
    cópia divergente.
    """
    existing = (
        await db_session.execute(select(JourneyStep).where(JourneyStep.key == _DEFAULT_STEP_KEY))
    ).scalar_one_or_none()
    if existing is not None:
        return existing

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


@pytest_asyncio.fixture
async def guardian_user(db_session: AsyncSession) -> User:
    """Uma conta de responsável mínima, válida, isolada por UUID único (RBAC do responsável)."""
    unique = uuid.uuid4().hex[:10]
    user = User(
        name="Responsável de Teste",
        email=f"guardian_{unique}@example.com",
        cpf=unique.ljust(11, "1")[:11],
        phone="11988887777",
        password_hash="not-a-real-hash",
        role=ROLE_GUARDIAN,
    )
    db_session.add(user)
    await db_session.flush()
    return user
