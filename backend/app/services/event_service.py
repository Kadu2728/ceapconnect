"""Regra de negócio de Eventos (EPIC 07).

Lista os próximos eventos (com status de inscrição) e permite inscrever/cancelar.
A inscrição gera uma notificação real para o candidato (USER_FLOW.md:
"Inscrição em Evento → Confirmação → Notificação enviada"). Tudo em uma única
transação atômica.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.event import Event
from app.models.user import User
from app.repositories.event_repository import EventRegistrationRepository, EventRepository
from app.schemas.event import (
    EventItem,
    EventListResponse,
    EventRegistrationResponse,
    EventSummary,
)
from app.services import notification_service
from app.services.candidate_profile_service import get_profile_or_raise


async def list_events(db: AsyncSession, user: User) -> EventListResponse:
    """Retorna os próximos eventos com o status de inscrição do candidato."""
    profile = await get_profile_or_raise(db, user)
    rows = await EventRepository(db).list_upcoming_with_registration_for_profile(profile.id)

    events = [_to_item(event, registered=registration is not None) for event, registration in rows]
    registered = sum(1 for item in events if item.registered)

    return EventListResponse(
        events=events,
        summary=EventSummary(total=len(events), registered=registered),
    )


async def register_event(
    db: AsyncSession, user: User, event_id: uuid.UUID
) -> EventRegistrationResponse:
    """Inscreve o candidato em um evento e emite a notificação de confirmação."""
    profile = await get_profile_or_raise(db, user)

    event = await EventRepository(db).get_by_id(event_id)
    if event is None:
        raise NotFoundException("Evento não encontrado.")

    registration_repo = EventRegistrationRepository(db)
    existing = await registration_repo.get(candidate_profile_id=profile.id, event_id=event_id)
    if existing is not None:
        raise ConflictException("Você já está inscrito neste evento.")

    await registration_repo.create(candidate_profile_id=profile.id, event_id=event_id)
    await notification_service.create_notification(
        db,
        candidate_profile_id=profile.id,
        title="Inscrição confirmada",
        description=f'Sua inscrição no evento "{event.title}" foi confirmada.',
        category="eventos",
    )
    await db.commit()

    return EventRegistrationResponse(event=_to_item(event, registered=True), registered=True)


async def cancel_registration(
    db: AsyncSession, user: User, event_id: uuid.UUID
) -> EventRegistrationResponse:
    """Cancela a inscrição do candidato em um evento."""
    profile = await get_profile_or_raise(db, user)

    event = await EventRepository(db).get_by_id(event_id)
    if event is None:
        raise NotFoundException("Evento não encontrado.")

    registration_repo = EventRegistrationRepository(db)
    registration = await registration_repo.get(candidate_profile_id=profile.id, event_id=event_id)
    if registration is None:
        raise ConflictException("Você não está inscrito neste evento.")

    await registration_repo.delete(registration)
    await db.commit()

    return EventRegistrationResponse(event=_to_item(event, registered=False), registered=False)


def _to_item(event: Event, *, registered: bool) -> EventItem:
    """Converte um `Event` do catálogo num item de API com o status de inscrição."""
    return EventItem(
        id=event.id,
        title=event.title,
        description=event.description,
        date=event.date,
        location=event.location,
        image_url=event.image_url,
        registered=registered,
    )
