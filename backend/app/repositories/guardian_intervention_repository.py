"""Acesso a dados da entidade `GuardianIntervention`.

Isola toda query relacionada a intervenções com responsáveis — a camada de
services nunca monta SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardian_intervention import GuardianIntervention
from app.models.intervention import InterventionChannel, InterventionOutcome


class GuardianInterventionRepository:
    """Repositório de leitura/escrita de intervenções com responsáveis."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        *,
        guardian_id: uuid.UUID,
        created_by_user_id: uuid.UUID | None,
        channel: InterventionChannel,
        outcome: InterventionOutcome,
        notes: str | None,
    ) -> GuardianIntervention:
        """Registra um contato (flush, sem commit)."""
        intervention = GuardianIntervention(
            guardian_id=guardian_id,
            created_by_user_id=created_by_user_id,
            channel=channel,
            outcome=outcome,
            notes=notes,
        )
        self._db.add(intervention)
        await self._db.flush()
        return intervention

    async def list_for_guardian(self, guardian_id: uuid.UUID) -> list[GuardianIntervention]:
        """Histórico de contatos com um responsável, mais recente primeiro."""
        stmt = (
            select(GuardianIntervention)
            .where(GuardianIntervention.guardian_id == guardian_id)
            .order_by(GuardianIntervention.created_at.desc())
        )
        return list((await self._db.execute(stmt)).scalars().all())
