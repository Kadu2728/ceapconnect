"""Acesso a dados das entidades `Event` e `EventRegistration` (EPIC 03/07).

Isola toda query relacionada a eventos e inscrições — a camada de services
nunca deve montar SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.event_registration import EventRegistration


class EventRepository:
    """Repositório de leitura do catálogo de `Event`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_upcoming(self, *, limit: int = 5) -> list[Event]:
        """Retorna os próximos eventos futuros (data > agora), mais próximos primeiro."""
        stmt = select(Event).where(Event.date > func.now()).order_by(Event.date.asc()).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, event_id: uuid.UUID) -> Event | None:
        """Busca um evento do catálogo pelo id."""
        return await self._db.get(Event, event_id)

    async def list_upcoming_with_registration_for_profile(
        self, candidate_profile_id: uuid.UUID
    ) -> list[tuple[Event, EventRegistration | None]]:
        """Retorna os eventos futuros com o status de inscrição do candidato.

        `EventRegistration` vem preenchido quando o candidato já está inscrito
        e `None` caso contrário (LEFT JOIN). Ordenado pela data (mais próximos
        primeiro).
        """
        stmt = (
            select(Event, EventRegistration)
            .outerjoin(
                EventRegistration,
                (EventRegistration.event_id == Event.id)
                & (EventRegistration.candidate_profile_id == candidate_profile_id),
            )
            .where(Event.date > func.now())
            .order_by(Event.date.asc())
        )
        result = await self._db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]


class EventRegistrationRepository:
    """Repositório de escrita das inscrições em eventos por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get(
        self, *, candidate_profile_id: uuid.UUID, event_id: uuid.UUID
    ) -> EventRegistration | None:
        """Busca a inscrição de um candidato em um evento específico."""
        stmt = select(EventRegistration).where(
            EventRegistration.candidate_profile_id == candidate_profile_id,
            EventRegistration.event_id == event_id,
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, *, candidate_profile_id: uuid.UUID, event_id: uuid.UUID
    ) -> EventRegistration:
        """Registra a inscrição de um candidato em um evento (flush, sem commit)."""
        registration = EventRegistration(
            candidate_profile_id=candidate_profile_id,
            event_id=event_id,
        )
        self._db.add(registration)
        await self._db.flush()
        return registration

    async def delete(self, registration: EventRegistration) -> None:
        """Remove uma inscrição existente (flush, sem commit)."""
        await self._db.delete(registration)
        await self._db.flush()
