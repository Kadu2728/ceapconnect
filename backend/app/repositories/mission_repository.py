"""Acesso a dados das entidades `Mission` e `MissionProgress` (EPIC 03/05).

Isola toda query relacionada a missões e ao progresso de missões por
candidato — a camada de services nunca deve montar SQL/ORM diretamente.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mission import Mission
from app.models.mission_progress import STATUS_COMPLETED, STATUS_PENDING, MissionProgress


class MissionRepository:
    """Repositório de leitura do catálogo de `Mission`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_all(self) -> list[Mission]:
        """Retorna todas as missões do catálogo, na ordem de criação."""
        stmt = select(Mission).order_by(Mission.created_at.asc())
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, mission_id: uuid.UUID) -> Mission | None:
        """Busca uma missão do catálogo pelo id."""
        return await self._db.get(Mission, mission_id)

    async def count_all(self) -> int:
        """Total de missões no catálogo — denominador da razão de conclusão (EPIC 14)."""
        stmt = select(func.count()).select_from(Mission)
        return int((await self._db.execute(stmt)).scalar_one())

    async def list_with_progress_for_profile(
        self, candidate_profile_id: uuid.UUID
    ) -> list[tuple[Mission, MissionProgress]]:
        """Retorna todas as missões do candidato com o respectivo progresso.

        Ordena as pendentes primeiro (prazo mais próximo antes; sem prazo por
        último) e as concluídas depois — a mesma prioridade de ação do
        Dashboard, agora para a tela completa de Missões.
        """
        stmt = (
            select(Mission, MissionProgress)
            .join(MissionProgress, MissionProgress.mission_id == Mission.id)
            .where(MissionProgress.candidate_profile_id == candidate_profile_id)
            .order_by(
                MissionProgress.completed_at.is_(None).desc(),
                Mission.due_date.asc().nulls_last(),
                Mission.created_at.asc(),
            )
        )
        result = await self._db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_next_pending_for_profile(
        self, candidate_profile_id: uuid.UUID
    ) -> tuple[Mission, MissionProgress] | None:
        """Retorna a próxima missão pendente do candidato.

        Prioridade: missões com prazo mais próximo primeiro; missões sem
        prazo (`due_date` nulo) ficam por último; em empate, prevalece a
        ordem de criação no catálogo.
        """
        stmt = (
            select(Mission, MissionProgress)
            .join(MissionProgress, MissionProgress.mission_id == Mission.id)
            .where(
                MissionProgress.candidate_profile_id == candidate_profile_id,
                MissionProgress.status == STATUS_PENDING,
            )
            .order_by(Mission.due_date.asc().nulls_last(), Mission.created_at.asc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        row = result.first()
        return (row[0], row[1]) if row is not None else None


class MissionProgressRepository:
    """Repositório de escrita do progresso de missões por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_profile_and_mission(
        self, *, candidate_profile_id: uuid.UUID, mission_id: uuid.UUID
    ) -> MissionProgress | None:
        """Busca o progresso de um candidato em uma missão específica."""
        stmt = select(MissionProgress).where(
            MissionProgress.candidate_profile_id == candidate_profile_id,
            MissionProgress.mission_id == mission_id,
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_completed_for_profile(self, candidate_profile_id: uuid.UUID) -> int:
        """Conta quantas missões o candidato já concluiu."""
        stmt = (
            select(func.count())
            .select_from(MissionProgress)
            .where(
                MissionProgress.candidate_profile_id == candidate_profile_id,
                MissionProgress.status == STATUS_COMPLETED,
            )
        )
        return int((await self._db.execute(stmt)).scalar_one())

    async def map_completed_count_for_profiles(
        self, candidate_profile_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        """Missões concluídas por candidato, em lote (EPIC 14 — feature de risco)."""
        if not candidate_profile_ids:
            return {}

        stmt = (
            select(MissionProgress.candidate_profile_id, func.count())
            .where(
                MissionProgress.candidate_profile_id.in_(candidate_profile_ids),
                MissionProgress.status == STATUS_COMPLETED,
            )
            .group_by(MissionProgress.candidate_profile_id)
        )
        rows = (await self._db.execute(stmt)).all()
        return {row[0]: int(row[1]) for row in rows}

    async def bulk_create_pending(
        self, *, candidate_profile_id: uuid.UUID, mission_ids: Sequence[uuid.UUID]
    ) -> None:
        """Cria uma linha `pending` para cada missão do catálogo informado.

        Chamado uma única vez, no registro do candidato (ver
        `app.services.candidate_profile_service.bootstrap_new_candidate`),
        para que o Dashboard sempre tenha uma "próxima missão" real.
        """
        if not mission_ids:
            return

        progresses = [
            MissionProgress(candidate_profile_id=candidate_profile_id, mission_id=mission_id)
            for mission_id in mission_ids
        ]
        self._db.add_all(progresses)
        await self._db.flush()
