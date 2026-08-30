"""Acesso a dados de `JourneyPause` (Pausa Declarada).

Isola as queries da pausa — a camada de services nunca monta SQL/ORM
diretamente.
"""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.journey_pause_rules import PauseReasonCode
from app.models.journey_pause import PAUSE_ACTIVE, JourneyPause, PauseStatus


class JourneyPauseRepository:
    """Repositório de leitura/escrita das pausas declaradas."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_active(self, candidate_profile_id: uuid.UUID) -> JourneyPause | None:
        """A pausa em curso deste candidato, se houver.

        Só pode existir uma (`uq_journey_pause_one_active`), por isso
        `scalar_one_or_none` é seguro aqui.
        """
        stmt = select(JourneyPause).where(
            JourneyPause.candidate_profile_id == candidate_profile_id,
            JourneyPause.status == PAUSE_ACTIVE,
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def get_active_now(
        self, candidate_profile_id: uuid.UUID, *, now: datetime
    ) -> JourneyPause | None:
        """A pausa em curso **e ainda dentro do prazo**.

        Distinta de `get_active`: uma pausa cujo prazo venceu não deve
        continuar valendo para o candidato só porque o job de expiração está
        atrasado. Filtrar por `ends_at` na query (e não em memória) mantém a
        leitura correta independentemente da cadência do job.
        """
        stmt = select(JourneyPause).where(
            JourneyPause.candidate_profile_id == candidate_profile_id,
            JourneyPause.status == PAUSE_ACTIVE,
            JourneyPause.ends_at > now,
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def set_paused_profile_ids(
        self, candidate_profile_ids: list[uuid.UUID]
    ) -> set[uuid.UUID]:
        """Quais destes candidatos estão em pausa agora — uma query para N ids.

        Existe para o job de lembretes, que percorre todos os candidatos
        ativos de uma vez: um `get_active` por candidato dentro do loop seria
        o N+1 que o job inteiro foi desenhado para evitar.
        """
        if not candidate_profile_ids:
            return set()
        stmt = select(JourneyPause.candidate_profile_id).where(
            JourneyPause.candidate_profile_id.in_(candidate_profile_ids),
            JourneyPause.status == PAUSE_ACTIVE,
        )
        return set((await self._db.execute(stmt)).scalars().all())

    async def list_due(self, *, now: datetime) -> list[JourneyPause]:
        """Pausas ativas cujo prazo já venceu (base do job de expiração)."""
        stmt = select(JourneyPause).where(
            JourneyPause.status == PAUSE_ACTIVE, JourneyPause.ends_at <= now
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def list_for_profile(self, candidate_profile_id: uuid.UUID) -> list[JourneyPause]:
        """Histórico completo de pausas do candidato, da mais recente para trás."""
        stmt = (
            select(JourneyPause)
            .where(JourneyPause.candidate_profile_id == candidate_profile_id)
            .order_by(JourneyPause.started_at.desc())
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def create(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        started_at: datetime,
        ends_at: datetime,
        requested_days: int,
        reason_code: PauseReasonCode | None,
        paused_at_step_key: str | None,
        resume_action_key: str | None,
    ) -> JourneyPause:
        """Cria a pausa (flush, sem commit — quem chama controla a transação)."""
        pause = JourneyPause(
            candidate_profile_id=candidate_profile_id,
            started_at=started_at,
            ends_at=ends_at,
            requested_days=requested_days,
            reason_code=reason_code,
            paused_at_step_key=paused_at_step_key,
            resume_action_key=resume_action_key,
            status=PAUSE_ACTIVE,
        )
        self._db.add(pause)
        await self._db.flush()
        return pause

    async def close(
        self, pause: JourneyPause, *, status: PauseStatus, ended_at: datetime
    ) -> JourneyPause:
        """Encerra a pausa com o desfecho informado (`resumed` ou `expired`)."""
        pause.status = status
        pause.ended_at = ended_at
        await self._db.flush()
        return pause
