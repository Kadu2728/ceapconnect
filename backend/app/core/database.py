"""Configuração do engine e das sessões assíncronas do SQLAlchemy.

Nenhuma query deve ser executada diretamente aqui — este módulo apenas
fornece a infraestrutura de conexão (engine, session factory e a
dependency `get_db` usada pelos routers via Depends).

**DATABASE_URL deve apontar para o endpoint *pooled* da Neon** (hostname com
sufixo `-pooler`, ex.: `ep-xxx-pooler.<region>.aws.neon.tech`) — o endpoint
direto abre uma conexão Postgres nova por request e estoura o limite de
conexões simultâneas sob carga, já que o Postgres serverless da Neon é bem
mais restrito nisso que um Postgres tradicional. Ver DEPLOY.md.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# O endpoint pooled da Neon é um PgBouncer em modo *transaction pooling*: a
# conexão física é devolvida ao pool assim que a transação termina, podendo
# ser reaproveitada por outra sessão lógica em seguida. Nesse modo, prepared
# statements do asyncpg (cacheados por conexão física, `PREPARE`/`DEALLOCATE`)
# vazam entre sessões diferentes e quebram sob concorrência
# (`DuplicatePreparedStatementError`/"prepared statement does not exist") —
# `statement_cache_size=0` desliga esse cache no driver, exigido pela própria
# Neon para asyncpg atrás do pooler. Sem custo perceptível: o ganho do pooler
# vem de reaproveitar a conexão física, não do cache de prepared statements.
_connect_args: dict[str, object] = {"statement_cache_size": 0}
if settings.database_ssl:
    _connect_args["ssl"] = True

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Classe base declarativa compartilhada por todos os models SQLAlchemy."""


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Dependency do FastAPI que fornece uma sessão de banco por request.

    Garante rollback automático em caso de exceção e fechamento da sessão
    ao final do ciclo de vida do request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
