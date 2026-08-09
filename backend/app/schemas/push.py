"""Schemas Pydantic de push notifications (EPIC 18 — PWA + push)."""

from pydantic import BaseModel, Field


class PushPublicKeyResponse(BaseModel):
    """Payload de `GET /api/v1/push/public-key`."""

    public_key: str
    configured: bool


class PushSubscribeRequest(BaseModel):
    """Corpo de `POST /api/v1/push/subscribe` — espelha `PushSubscription.toJSON()`
    do navegador (`endpoint` + `keys.p256dh`/`keys.auth`)."""

    endpoint: str = Field(min_length=1)
    p256dh: str = Field(min_length=1)
    auth: str = Field(min_length=1)


class PushUnsubscribeRequest(BaseModel):
    """Corpo de `POST /api/v1/push/unsubscribe`."""

    endpoint: str = Field(min_length=1)
