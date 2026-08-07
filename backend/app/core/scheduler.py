"""Job agendado de recálculo de risco (EPIC 14 — fase 3).

Roda **in-process**, dentro do mesmo processo web (via `APScheduler` /
`AsyncIOScheduler`) — o Render free/starter não tem um processo "worker"
separado, então o job precisa conviver com a API no mesmo processo, sem
travar o event loop principal (por isso é assíncrono, nunca uma thread ou
chamada bloqueante).

Abre sua própria sessão de banco a cada execução — nunca reaproveita a sessão
de um request (`get_db`), porque o job não está associado a nenhum request e
roda de forma **desacoplada da experiência do usuário** (requisito da spec).
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services import risk_service

logger = logging.getLogger("ceap_connect.scheduler")

_scheduler: AsyncIOScheduler | None = None
_JOB_ID = "risk-recompute"


async def _run_recompute() -> None:
    """Executa um ciclo de recálculo, numa sessão de banco própria do job.

    Qualquer falha é logada e contida aqui — nunca propaga a ponto de derrubar
    o scheduler ou o processo web.
    """
    async with AsyncSessionLocal() as db:
        try:
            summary = await risk_service.recompute_all(db)
            logger.info(
                "Recálculo de risco concluído: %d candidato(s) processado(s), "
                "%d intervenção(ões) medida(s), %.2fs.",
                summary.candidates_processed,
                summary.interventions_measured,
                summary.duration_seconds,
            )
        except Exception:  # noqa: BLE001 — o job nunca pode derrubar o processo web
            logger.exception("Falha no recálculo agendado de risco")
            await db.rollback()


def start_scheduler() -> None:
    """Inicia o job periódico. Chamado no `lifespan` de startup do FastAPI.

    Idempotente (chamar duas vezes não duplica o job — útil sob reload).
    """
    global _scheduler
    if _scheduler is not None:
        return

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        _run_recompute,
        trigger="interval",
        minutes=settings.risk_recompute_interval_minutes,
        id=_JOB_ID,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=60,
    )
    scheduler.start()
    _scheduler = scheduler

    # Primeira execução logo após o boot, em background (não atrasa o startup
    # do app) — sem isso, a fila de risco ficaria vazia até o 1º intervalo
    # completo, o que é ruim tanto para produção quanto para demonstração.
    asyncio.create_task(_run_recompute())  # noqa: RUF006 — fire-and-forget intencional

    logger.info(
        "Job de recálculo de risco agendado a cada %d minuto(s).",
        settings.risk_recompute_interval_minutes,
    )


def shutdown_scheduler() -> None:
    """Encerra o job. Chamado no `lifespan` de shutdown do FastAPI."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
