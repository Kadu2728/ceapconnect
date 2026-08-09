"""Acesso a dados das estatísticas de coorte (EPIC 20 — percentil sem ranking).

Isola as queries agregadas usadas para situar o candidato dentro da própria
turma. Deliberadamente só agrega: nenhuma consulta aqui retorna identidade de
outro candidato — ver `cohort_stats_service` para o racional.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import CandidateProfile
from app.models.user import ROLE_CANDIDATE, User

_MIN_COHORT_SIZE = 5


class CohortStatsRepository:
    """Estatísticas agregadas da coorte de um candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def xp_standing(self, *, cohort_id: uuid.UUID, xp_total: int) -> tuple[int, int]:
        """Retorna `(total_de_candidatos, quantos_tem_xp_menor_ou_igual)` na coorte.

        Uma única query com `count(*) FILTER (...)` em vez de duas — o percentil
        é derivado disso no service, nunca no SQL (ver `cohort_stats_service`).
        """
        stmt = (
            select(
                func.count().label("total"),
                func.count().filter(CandidateProfile.xp_total <= xp_total).label("at_or_below"),
            )
            .select_from(CandidateProfile)
            .join(User, User.id == CandidateProfile.user_id)
            .where(
                CandidateProfile.cohort_id == cohort_id,
                CandidateProfile.deleted_at.is_(None),
                User.deleted_at.is_(None),
                User.role == ROLE_CANDIDATE,
            )
        )
        row = (await self._db.execute(stmt)).one()
        return int(row.total), int(row.at_or_below)
