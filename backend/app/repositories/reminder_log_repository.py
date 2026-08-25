"""Acesso a dados da entidade `ReminderLog` (lembretes automáticos).

Isola a query "quem já recebeu este lembrete" — sempre em lote, nunca um
candidato por vez, pelo mesmo motivo de `risk_feature_service`: o job
percorre todos os candidatos ativos a cada ciclo.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder_log import ReminderLog, ReminderType


class ReminderLogRepository:
    """Repositório de leitura/escrita do log de lembretes já enviados."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def set_sent_profile_ids(
        self, candidate_profile_ids: list[uuid.UUID], *, reminder_type: ReminderType
    ) -> set[uuid.UUID]:
        """Quais destes candidatos já receberam este tipo de lembrete, em lote."""
        if not candidate_profile_ids:
            return set()

        stmt = select(ReminderLog.candidate_profile_id).where(
            ReminderLog.candidate_profile_id.in_(candidate_profile_ids),
            ReminderLog.reminder_type == reminder_type,
        )
        rows = (await self._db.execute(stmt)).scalars().all()
        return set(rows)

    async def create(
        self, *, candidate_profile_id: uuid.UUID, reminder_type: ReminderType
    ) -> ReminderLog:
        """Registra o envio (flush, sem commit — quem chama controla a transação)."""
        log = ReminderLog(candidate_profile_id=candidate_profile_id, reminder_type=reminder_type)
        self._db.add(log)
        await self._db.flush()
        return log
