"""Acesso a dados das estatísticas de coorte (EPIC 20 — percentil sem ranking).

Isola as queries agregadas usadas para situar o candidato dentro da própria
turma. Deliberadamente só agrega: nenhuma consulta aqui retorna identidade de
outro candidato — ver `cohort_stats_service` para o racional.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cohort_xp_standing import CohortXpStanding


class CohortStatsRepository:
    """Estatísticas agregadas da coorte de um candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def xp_standing(self, *, candidate_profile_id: uuid.UUID) -> tuple[int, int] | None:
        """Lê `(total_de_candidatos, quantos_tem_xp_menor_ou_igual)` pré-calculado.

        Fonte é a materialized view `cohort_xp_standing` (Fase 4 — otimizações
        medidas: antes, esta era uma agregação ao vivo sobre toda a coorte em
        **toda** carga do Dashboard; agora é uma leitura indexada por
        `candidate_profile_id`, atualizada periodicamente pelo scheduler).
        `None` = candidato ainda não entrou no último refresh (coorte
        nova/atribuição recente) — o service trata igual a qualquer outro caso
        sem dado suficiente (nenhuma faixa exibida).
        """
        stmt = select(CohortXpStanding.total, CohortXpStanding.at_or_below).where(
            CohortXpStanding.candidate_profile_id == candidate_profile_id
        )
        row = (await self._db.execute(stmt)).one_or_none()
        return (int(row.total), int(row.at_or_below)) if row is not None else None
