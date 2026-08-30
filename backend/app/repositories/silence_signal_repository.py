"""Acesso a dados de `SilenceSignal` (Radar de Silêncio).

Desenhado para lote, como `risk_feature_service`: o Radar roda dentro do job
de recálculo de risco, que percorre todos os candidatos ativos — uma query
por candidato inviabilizaria o job.
"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.silence_signal import SilenceSignal


class SilenceSignalRepository:
    """Repositório de leitura/escrita dos sinais de silêncio."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def map_open_by_profile_ids(
        self, candidate_profile_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, SilenceSignal]:
        """Sinais em aberto de vários candidatos de uma vez (evita N+1 no job)."""
        if not candidate_profile_ids:
            return {}
        stmt = select(SilenceSignal).where(
            SilenceSignal.candidate_profile_id.in_(candidate_profile_ids),
            SilenceSignal.returned_at.is_(None),
        )
        rows = (await self._db.execute(stmt)).scalars().all()
        return {signal.candidate_profile_id: signal for signal in rows}

    async def count_detected_since(self, *, since: datetime) -> int:
        """Quantas travessias para o silêncio aconteceram desde `since`.

        É a métrica que o Console mostra: "N entraram em silêncio esta
        semana" — contagem de *pessoas que cruzaram*, não de quem está
        silencioso (isso a fila inteira já mostra).
        """
        stmt = (
            select(func.count())
            .select_from(SilenceSignal)
            .where(SilenceSignal.detected_at >= since)
        )
        return (await self._db.execute(stmt)).scalar_one()

    async def create(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        detected_at: datetime,
        days_silent: float,
        step_key: str | None,
    ) -> SilenceSignal:
        """Abre um sinal (flush, sem commit — quem chama controla a transação)."""
        signal = SilenceSignal(
            candidate_profile_id=candidate_profile_id,
            detected_at=detected_at,
            days_silent=days_silent,
            step_key=step_key,
        )
        self._db.add(signal)
        await self._db.flush()
        return signal

    async def close(self, signal: SilenceSignal, *, returned_at: datetime) -> SilenceSignal:
        """Fecha o sinal porque o candidato voltou a dar sinal de vida."""
        signal.returned_at = returned_at
        await self._db.flush()
        return signal
