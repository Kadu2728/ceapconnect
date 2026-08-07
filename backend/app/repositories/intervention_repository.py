"""Acesso a dados da entidade `Intervention` (EPIC 14 — Predição de evasão).

Isola as queries de intervenção — a camada de services nunca monta SQL/ORM
diretamente.
"""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intervention import Intervention, InterventionChannel, InterventionOutcome


class InterventionRepository:
    """Repositório de leitura/escrita de intervenções de coordenadores."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        created_by_user_id: uuid.UUID,
        channel: InterventionChannel,
        outcome: InterventionOutcome,
        notes: str | None,
        score_at_creation: int,
    ) -> Intervention:
        """Registra uma intervenção (flush, sem commit)."""
        intervention = Intervention(
            candidate_profile_id=candidate_profile_id,
            created_by_user_id=created_by_user_id,
            channel=channel,
            outcome=outcome,
            notes=notes,
            score_at_creation=score_at_creation,
        )
        self._db.add(intervention)
        await self._db.flush()
        return intervention

    async def list_for_candidate(self, candidate_profile_id: uuid.UUID) -> list[Intervention]:
        """Histórico de intervenções de um candidato, mais recentes primeiro."""
        stmt = (
            select(Intervention)
            .where(Intervention.candidate_profile_id == candidate_profile_id)
            .order_by(Intervention.created_at.desc())
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def list_due_for_measurement(self, *, before: datetime) -> list[Intervention]:
        """Intervenções com 7+ dias e ainda não medidas — usado pelo job agendado."""
        stmt = select(Intervention).where(
            Intervention.created_at <= before,
            Intervention.measured_at.is_(None),
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def mark_measured(
        self,
        intervention: Intervention,
        *,
        measured_at: datetime,
        score_after: int,
        had_activity_after: bool,
    ) -> None:
        """Preenche o resultado da medição de impacto (flush, sem commit)."""
        intervention.measured_at = measured_at
        intervention.score_after = score_after
        intervention.had_activity_after = had_activity_after
        await self._db.flush()
