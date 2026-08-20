"""Cliente Redis opcional (Fase 4 — otimizações medidas).

Cache é estritamente um acelerador, nunca uma dependência: sem `REDIS_URL`
configurado, ou se qualquer operação falhar (Upstash fora do ar, rede,
timeout), o app funciona exatamente como sem cache — nunca propaga erro para
quem chamou. Mesmo princípio de "nunca quebra a experiência" já usado em
`app.services.activity_event_service`.

Compatível com Upstash Redis direto: `redis.asyncio.Redis.from_url` entende o
esquema `rediss://` (TLS) que a Upstash fornece, sem SDK proprietário.
"""

import logging
from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger("ceap_connect.cache")

_SOCKET_TIMEOUT_SECONDS = 2.0


@lru_cache
def _get_client() -> Redis | None:
    """Cliente singleton, ou `None` se `REDIS_URL` não estiver configurado.

    Timeout curto de propósito: uma leitura de cache não pode custar mais que
    a query que ela substituiria — se o Redis não responder rápido, é melhor
    seguir sem cache do que travar o request esperando.
    """
    if not settings.redis_url:
        return None
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_timeout=_SOCKET_TIMEOUT_SECONDS,
        socket_connect_timeout=_SOCKET_TIMEOUT_SECONDS,
    )


async def get_cached(key: str) -> str | None:
    """Lê uma chave do cache. `None` tanto para "não configurado" quanto para "miss"."""
    client = _get_client()
    if client is None:
        return None
    try:
        return await client.get(key)
    except Exception:  # noqa: BLE001 — cache nunca pode quebrar quem chamou
        logger.warning("Falha ao ler cache (%s) — seguindo sem cache.", key, exc_info=True)
        return None


async def set_cached(key: str, value: str, *, ttl_seconds: int) -> None:
    """Grava uma chave com expiração. Silenciosamente ignora se não configurado/falhar."""
    client = _get_client()
    if client is None:
        return
    try:
        await client.set(key, value, ex=ttl_seconds)
    except Exception:  # noqa: BLE001 — cache nunca pode quebrar quem chamou
        logger.warning("Falha ao gravar cache (%s) — seguindo sem cache.", key, exc_info=True)
