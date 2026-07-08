"""Acesso a dados da entidade `JourneyStep` (EPIC 03/04 — Dashboard/Jornada).

Catálogo fixo — apenas leitura nesta fase (o seed é o único "escritor").
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.journey_step import JourneyStep


class JourneyStepRepository:
    """Repositório de leitura da entidade `JourneyStep`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_ordered(self) -> list[JourneyStep]:
        """Retorna todas as etapas do catálogo, ordenadas por `order`."""
        stmt = select(JourneyStep).order_by(JourneyStep.order.asc())
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_order(self, order: int) -> JourneyStep | None:
        """Busca uma etapa pela sua posição na jornada (1-indexed)."""
        stmt = select(JourneyStep).where(JourneyStep.order == order)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()
