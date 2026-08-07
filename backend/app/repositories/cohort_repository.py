"""Acesso a dados de coortes e do vínculo coordenador ↔ coorte (EPIC 14).

Isola as queries que sustentam o escopo do RBAC — a camada de services nunca
monta SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cohort import Cohort, CoordinatorCohort


class CohortRepository:
    """Repositório do catálogo de coortes."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_all(self, *, only_active: bool = False) -> list[Cohort]:
        """Coortes cadastradas, mais recentes primeiro (ano/semestre)."""
        stmt = select(Cohort).order_by(Cohort.year.desc(), Cohort.term.desc())
        if only_active:
            stmt = stmt.where(Cohort.is_active.is_(True))
        return list((await self._db.execute(stmt)).scalars().all())

    async def get_by_id(self, cohort_id: uuid.UUID) -> Cohort | None:
        """Uma coorte pelo id."""
        stmt = select(Cohort).where(Cohort.id == cohort_id)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def get_by_year_term(self, *, year: int, term: str) -> Cohort | None:
        """Uma coorte pela chave natural (ano + semestre) — usada pelo seed."""
        stmt = select(Cohort).where(Cohort.year == year, Cohort.term == term)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def list_cohort_ids_for_coordinator(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        """Ids das coortes vinculadas a um coordenador (escopo de acesso).

        Lista vazia = coordenador sem coorte atribuída: por segurança, isso
        significa "não enxerga nenhum candidato" (nunca "enxerga todos").
        """
        stmt = select(CoordinatorCohort.cohort_id).where(CoordinatorCohort.user_id == user_id)
        return list((await self._db.execute(stmt)).scalars().all())

    async def assign_coordinator(
        self, *, user_id: uuid.UUID, cohort_id: uuid.UUID
    ) -> CoordinatorCohort:
        """Vincula um coordenador a uma coorte (flush, sem commit)."""
        link = CoordinatorCohort(user_id=user_id, cohort_id=cohort_id)
        self._db.add(link)
        await self._db.flush()
        return link
