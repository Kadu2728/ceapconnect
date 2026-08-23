"""Acesso a dados do funil de conversão da jornada (KPI inscrição→prova).

Isola a query de contagem por etapa — a camada de services nunca monta
SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import CandidateProfile
from app.models.journey_step import JourneyStep
from app.models.user import ROLE_CANDIDATE, User


class FunnelRepository:
    """Contagem de candidatos por etapa atual da jornada."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def count_by_current_step_order(
        self, *, cohort_ids: list[uuid.UUID] | None
    ) -> dict[int, int]:
        """Quantos candidatos ativos estão exatamente em cada `order` de etapa hoje.

        `cohort_ids=None` = irrestrito (admin). Lista (mesmo vazia) restringe
        às coortes informadas — lista vazia sempre retorna vazio, nunca
        "todos" (mesma semântica de `CohortScope`).
        """
        if cohort_ids is not None and len(cohort_ids) == 0:
            return {}

        stmt = (
            select(JourneyStep.order, func.count(CandidateProfile.id))
            .select_from(CandidateProfile)
            .join(User, User.id == CandidateProfile.user_id)
            .join(JourneyStep, JourneyStep.key == CandidateProfile.current_journey_step_key)
            .where(
                CandidateProfile.deleted_at.is_(None),
                User.deleted_at.is_(None),
                User.role == ROLE_CANDIDATE,
            )
            .group_by(JourneyStep.order)
        )
        if cohort_ids is not None:
            stmt = stmt.where(CandidateProfile.cohort_id.in_(cohort_ids))

        rows = (await self._db.execute(stmt)).all()
        return {int(row[0]): int(row[1]) for row in rows}
