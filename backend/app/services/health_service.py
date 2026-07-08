"""Regra de negócio do health check.

Isolado em service para manter o router livre de qualquer lógica além de
request/response, conforme BACKEND_GUIDELINES.md.
"""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.health import HealthData

logger = logging.getLogger("ceap_connect")


async def get_health_status(db: AsyncSession) -> HealthData:
    """Verifica a saúde da aplicação, incluindo a conectividade com o banco."""
    database_status = "up"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Falha ao conectar ao banco de dados durante o health check")
        database_status = "down"

    return HealthData(
        status="ok" if database_status == "up" else "degraded",
        version=settings.app_version,
        database=database_status,
    )
