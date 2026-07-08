"""Schemas de response da feature Eventos (EPIC 07).

Espelham o contrato consumido pelo frontend (`features/events`). Cada item
traz o evento do catálogo com o status de inscrição do candidato.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class EventItem(BaseModel):
    """Um evento do catálogo com o status de inscrição do candidato."""

    id: uuid.UUID
    title: str
    description: str
    date: datetime
    location: str
    image_url: str | None
    registered: bool


class EventSummary(BaseModel):
    """Resumo dos eventos do candidato."""

    total: int
    registered: int


class EventListResponse(BaseModel):
    """Corpo de `GET /api/v1/events`."""

    events: list[EventItem]
    summary: EventSummary


class EventRegistrationResponse(BaseModel):
    """Corpo de `POST`/`DELETE /api/v1/events/{id}/register`."""

    event: EventItem
    registered: bool
