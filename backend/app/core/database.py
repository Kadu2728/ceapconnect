"""Configuração do engine e das sessões assíncronas do SQLAlchemy.

Nenhuma query deve ser executada diretamente aqui — este módulo apenas
fornece a infraestrutura de conexão (engine, session factory e a
dependency `get_db` usada pelos routers via Depends).
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args={"ssl": True} if settings.database_ssl else {},
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
