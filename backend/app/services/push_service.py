"""Push notifications reais via Web Push (EPIC 18 — PWA + push).

Usa o protocolo padrão Web Push (autenticado via VAPID) — suportado
nativamente por todo navegador moderno, sem SDK nem serviço pago (ao
contrário de e-mail/SMS, que dependem de um provedor terceiro). O par de
chaves VAPID é gerado uma vez (`py-vapid`) e configurado via `.env`.

Degradação graciosa: sem `VAPID_PUBLIC_KEY`/`VAPID_PRIVATE_KEY`, o envio
simplesmente não acontece — a inscrição (`subscribe`) já recusa antes, e o
app continua instalável/funcional sem push.

Best-effort: enviar um push nunca pode quebrar o fluxo de negócio que criou a
notificação (mesmo racional de `activity_event_service.track`). Uma
inscrição que responde 404/410 (expirada/revogada pelo navegador) é
removida automaticamente.
"""

import json
import logging
import uuid

from pywebpush import WebPushException, webpush_async
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.repositories.push_subscription_repository import PushSubscriptionRepository
from app.services.candidate_profile_service import get_profile_or_raise

logger = logging.getLogger("ceap_connect.push")

_EXPIRED_STATUS_CODES = {404, 410}


def is_configured() -> bool:
    """Indica se o par de chaves VAPID está configurado."""
    return bool(settings.vapid_public_key.strip() and settings.vapid_private_key.strip())


def get_public_key() -> str:
    """Chave pública VAPID, enviada ao navegador para a inscrição no push."""
    return settings.vapid_public_key


async def subscribe(db: AsyncSession, user: User, *, endpoint: str, p256dh: str, auth: str) -> None:
    """Registra (ou atualiza) a inscrição de push de um dispositivo. Commita."""
    profile = await get_profile_or_raise(db, user)
    await PushSubscriptionRepository(db).upsert(
        candidate_profile_id=profile.id, endpoint=endpoint, p256dh=p256dh, auth=auth
    )
    await db.commit()


async def unsubscribe(db: AsyncSession, user: User, *, endpoint: str) -> None:
    """Remove a inscrição de push de um dispositivo. Commita."""
    profile = await get_profile_or_raise(db, user)
    await PushSubscriptionRepository(db).delete_by_endpoint(
        candidate_profile_id=profile.id, endpoint=endpoint
    )
    await db.commit()


async def send_push_to_profile(
    db: AsyncSession, candidate_profile_id: uuid.UUID, *, title: str, body: str, url: str = "/"
) -> None:
    """Envia um push para todos os dispositivos inscritos do candidato.

    Best-effort: nunca levanta exceção. Sem chaves VAPID configuradas, é um
    no-op silencioso (a notificação in-app já foi criada por quem chamou).
    """
    if not is_configured():
        return

    repo = PushSubscriptionRepository(db)
    subscriptions = await repo.list_for_profile(candidate_profile_id)
    if not subscriptions:
        return

    payload = json.dumps({"title": title, "body": body, "url": url})

    for subscription in subscriptions:
        try:
            await webpush_async(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                },
                data=payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_subject},
            )
        except WebPushException as exc:
            status = getattr(exc.response, "status", None)
            if status in _EXPIRED_STATUS_CODES:
                await repo.delete_by_endpoint_only(subscription.endpoint)
            else:
                logger.warning("Falha ao enviar push (status=%s): %s", status, exc)
        except Exception:  # noqa: BLE001 — push jamais quebra o fluxo de negócio
            logger.exception("Falha inesperada ao enviar push")

    await db.flush()
