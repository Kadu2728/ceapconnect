"""Acesso a dados da entidade `ActivityEvent` (EPIC 14 — fase 2).

Isola as queries do log comportamental. Todas as leituras aqui são desenhadas
para usar o índice composto `(candidate_profile_id, occurred_at)` — a derivação
de features (fase 3) percorre muitos candidatos e não pode degradar para full
scan.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_event import (
    EVENT_DOCUMENT_UPLOADED,
    EVENT_MISSION_COMPLETED,
    EVENT_STEP_VIEWED,
    ActivityEvent,
    ActivityEventName,
)


class ActivityEventRepository:
    """Repositório de escrita/leitura do log de eventos comportamentais."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        name: ActivityEventName,
        props: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> ActivityEvent:
        """Registra um evento (flush, sem commit — quem chama controla a transação)."""
        event = ActivityEvent(
            candidate_profile_id=candidate_profile_id,
            name=name,
            props=props or {},
        )
        if occurred_at is not None:
            event.occurred_at = occurred_at
        self._db.add(event)
        await self._db.flush()
        return event

    async def get_last_occurred_at(self, candidate_profile_id: uuid.UUID) -> datetime | None:
        """Instante do evento mais recente do candidato (base de "dias sem atividade")."""
        stmt = (
            select(ActivityEvent.occurred_at)
            .where(ActivityEvent.candidate_profile_id == candidate_profile_id)
            .order_by(ActivityEvent.occurred_at.desc())
            .limit(1)
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def count_by_name_for_profile(
        self, candidate_profile_id: uuid.UUID, *, since: datetime | None = None
    ) -> dict[str, int]:
        """Contagem de eventos por nome para um candidato (opcionalmente desde `since`)."""
        stmt = (
            select(ActivityEvent.name, func.count())
            .where(ActivityEvent.candidate_profile_id == candidate_profile_id)
            .group_by(ActivityEvent.name)
        )
        if since is not None:
            stmt = stmt.where(ActivityEvent.occurred_at >= since)

        rows = (await self._db.execute(stmt)).all()
        return {row[0]: int(row[1]) for row in rows}

    async def count_by_names(
        self, names: list[ActivityEventName], *, since: datetime | None = None
    ) -> dict[str, int]:
        """Contagem global de eventos por nome, sem filtro de candidato.

        Base do Learning Loop (F2 — `journey_os_metrics_service`): CTR do
        Next Best Action e taxa de retomada do Modo Resgate são métricas de
        produto, não por candidato/coorte, então esta é a única leitura
        deste repositório que não recebe `candidate_profile_id(s)`.
        """
        if not names:
            return {}

        stmt = (
            select(ActivityEvent.name, func.count())
            .where(ActivityEvent.name.in_(names))
            .group_by(ActivityEvent.name)
        )
        if since is not None:
            stmt = stmt.where(ActivityEvent.occurred_at >= since)

        rows = (await self._db.execute(stmt)).all()
        return {row[0]: int(row[1]) for row in rows}

    async def list_recent_for_profile(
        self, candidate_profile_id: uuid.UUID, *, limit: int = 100
    ) -> list[ActivityEvent]:
        """Eventos mais recentes do candidato (timeline do console de intervenção)."""
        stmt = (
            select(ActivityEvent)
            .where(ActivityEvent.candidate_profile_id == candidate_profile_id)
            .order_by(ActivityEvent.occurred_at.desc())
            .limit(limit)
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def map_last_occurred_at(
        self, candidate_profile_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, datetime]:
        """Última atividade de vários candidatos de uma vez (evita N+1 no job).

        Uma única query agregada para todo o lote — o job de recálculo percorre
        centenas/milhares de candidatos e não pode fazer uma query por candidato.
        """
        if not candidate_profile_ids:
            return {}

        stmt = (
            select(
                ActivityEvent.candidate_profile_id,
                func.max(ActivityEvent.occurred_at),
            )
            .where(ActivityEvent.candidate_profile_id.in_(candidate_profile_ids))
            .group_by(ActivityEvent.candidate_profile_id)
        )
        rows = (await self._db.execute(stmt)).all()
        return {row[0]: row[1] for row in rows}

    async def map_event_count_by_name(
        self, candidate_profile_ids: list[uuid.UUID], *, name: ActivityEventName
    ) -> dict[uuid.UUID, int]:
        """Contagem de um evento específico (ex.: `mission_abandoned`) por candidato, em lote."""
        if not candidate_profile_ids:
            return {}

        stmt = (
            select(ActivityEvent.candidate_profile_id, func.count())
            .where(
                ActivityEvent.candidate_profile_id.in_(candidate_profile_ids),
                ActivityEvent.name == name,
            )
            .group_by(ActivityEvent.candidate_profile_id)
        )
        rows = (await self._db.execute(stmt)).all()
        return {row[0]: int(row[1]) for row in rows}

    async def map_completion_timestamps(
        self, candidate_profile_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[datetime]]:
        """Timestamps de `mission_completed` por candidato, em ordem crescente.

        Base do cálculo de "velocidade média entre etapas" — a diferença entre
        conclusões consecutivas mede o ritmo do candidato.
        """
        if not candidate_profile_ids:
            return {}

        stmt = (
            select(ActivityEvent.candidate_profile_id, ActivityEvent.occurred_at)
            .where(
                ActivityEvent.candidate_profile_id.in_(candidate_profile_ids),
                ActivityEvent.name == EVENT_MISSION_COMPLETED,
            )
            .order_by(ActivityEvent.candidate_profile_id, ActivityEvent.occurred_at.asc())
        )
        rows = (await self._db.execute(stmt)).all()

        result: dict[uuid.UUID, list[datetime]] = {}
        for profile_id, occurred_at in rows:
            result.setdefault(profile_id, []).append(occurred_at)
        return result

    async def map_first_step_viewed_at(
        self, candidate_profile_ids: list[uuid.UUID]
    ) -> dict[tuple[uuid.UUID, str], datetime]:
        """Primeiro `step_viewed` de cada (candidato, etapa) — proxy de "desde quando
        está nesta etapa", usado para detectar se o candidato está travado.
        """
        if not candidate_profile_ids:
            return {}

        step_key = ActivityEvent.props["step_key"].astext
        stmt = (
            select(
                ActivityEvent.candidate_profile_id,
                step_key,
                func.min(ActivityEvent.occurred_at),
            )
            .where(
                ActivityEvent.candidate_profile_id.in_(candidate_profile_ids),
                ActivityEvent.name == EVENT_STEP_VIEWED,
                step_key.is_not(None),
            )
            .group_by(ActivityEvent.candidate_profile_id, step_key)
        )
        rows = (await self._db.execute(stmt)).all()
        return {(row[0], row[1]): row[2] for row in rows}

    async def set_profiles_with_document_uploaded(
        self, candidate_profile_ids: list[uuid.UUID]
    ) -> set[uuid.UUID]:
        """Ids de candidatos com ao menos um `document_uploaded` registrado."""
        if not candidate_profile_ids:
            return set()

        stmt = (
            select(ActivityEvent.candidate_profile_id)
            .where(
                ActivityEvent.candidate_profile_id.in_(candidate_profile_ids),
                ActivityEvent.name == EVENT_DOCUMENT_UPLOADED,
            )
            .distinct()
        )
        rows = (await self._db.execute(stmt)).scalars().all()
        return set(rows)
