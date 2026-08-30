"""Jobs agendados in-process: recálculo de risco (EPIC 14) e refresh da
materialized view de percentil de XP (Fase 4 — otimizações medidas).

Rodam **in-process**, dentro do mesmo processo web (via `APScheduler` /
`AsyncIOScheduler`) — o Render free/starter não tem um processo "worker"
separado, então os jobs precisam conviver com a API no mesmo processo, sem
travar o event loop principal (por isso são assíncronos, nunca uma thread ou
chamada bloqueante).

Cada job abre sua própria sessão de banco a cada execução — nunca reaproveita
a sessão de um request (`get_db`), porque nenhum dos dois está associado a um
request e rodam de forma **desacoplada da experiência do usuário**.
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services import journey_pause_service, reminder_service, risk_service

logger = logging.getLogger("ceap_connect.scheduler")

_scheduler: AsyncIOScheduler | None = None
_RISK_JOB_ID = "risk-recompute"
_COHORT_XP_JOB_ID = "cohort-xp-standing-refresh"
_REMINDER_JOB_ID = "reminder-check"


async def _run_recompute() -> None:
    """Executa um ciclo de recálculo de risco, numa sessão de banco própria do job.

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


async def _run_reminder_check() -> None:
    """Expira pausas declaradas vencidas e, em seguida, verifica os lembretes.

    A ordem importa, e por isso os dois moram no mesmo job: uma pausa vencida
    precisa parar de suprimir a cobrança de documentação **já nesta passada**.
    Um terceiro job só para expirar pausas disputaria o processo único do
    plano free do Render sem ganhar nada — o único consumidor que depende de
    expiração pontual é justamente o lembrete (a leitura do candidato já
    ignora pausa vencida por conta própria, ver `get_active_now`).

    Qualquer falha é logada e contida aqui — nunca propaga a ponto de derrubar
    o scheduler ou o processo web (mesmo racional de `_run_recompute`).
    """
    async with AsyncSessionLocal() as db:
        try:
            expired = await journey_pause_service.expire_due_pauses(db)
            if expired:
                logger.info("%d pausa(s) declarada(s) expirada(s).", expired)

            summary = await reminder_service.check_and_send_reminders(db)
            logger.info(
                "Verificação de lembretes concluída: %d candidato(s) checado(s), "
                "%d lembrete(s) enviado(s), %.2fs.",
                summary.candidates_checked,
                summary.reminders_sent,
                summary.duration_seconds,
            )
        except Exception:  # noqa: BLE001 — o job nunca pode derrubar o processo web
            logger.exception("Falha na verificação agendada de lembretes")
            await db.rollback()


async def _run_cohort_xp_refresh() -> None:
    """Atualiza `cohort_xp_standing` (materialized view lida em toda carga do Dashboard).

    `REFRESH MATERIALIZED VIEW` simples (sem `CONCURRENTLY`): a view é pequena
    (uma linha por candidato) e o lock de escrita dura milissegundos — na
    escala desta aplicação, a complexidade extra de `CONCURRENTLY` (exige
    índice único, execução fora de transação) não se paga.
    """
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("REFRESH MATERIALIZED VIEW cohort_xp_standing"))
            await db.commit()
            logger.info("Materialized view cohort_xp_standing atualizada.")
        except Exception:  # noqa: BLE001 — o job nunca pode derrubar o processo web
            logger.exception("Falha ao atualizar cohort_xp_standing")
            await db.rollback()


def start_scheduler() -> None:
    """Inicia os jobs periódicos. Chamado no `lifespan` de startup do FastAPI.

    Idempotente (chamar duas vezes não duplica os jobs — útil sob reload).
    """
    global _scheduler
    if _scheduler is not None:
        return

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        _run_recompute,
        trigger="interval",
        minutes=settings.risk_recompute_interval_minutes,
        id=_RISK_JOB_ID,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=60,
    )
    scheduler.add_job(
        _run_cohort_xp_refresh,
        trigger="interval",
        minutes=settings.cohort_xp_refresh_interval_minutes,
        id=_COHORT_XP_JOB_ID,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=60,
    )
    scheduler.add_job(
        _run_reminder_check,
        trigger="interval",
        minutes=settings.reminder_check_interval_minutes,
        id=_REMINDER_JOB_ID,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=60,
    )
    scheduler.start()
    _scheduler = scheduler

    # Primeira execução de cada job logo após o boot, em background (não
    # atrasa o startup do app) — sem isso, a fila de risco e o percentil de
    # XP ficariam vazios até o 1º intervalo completo, ruim tanto para
    # produção quanto para demonstração.
    asyncio.create_task(_run_recompute())  # noqa: RUF006 — fire-and-forget intencional
    asyncio.create_task(_run_cohort_xp_refresh())  # noqa: RUF006 — fire-and-forget intencional
    asyncio.create_task(_run_reminder_check())  # noqa: RUF006 — fire-and-forget intencional

    logger.info(
        "Job de recálculo de risco agendado a cada %d minuto(s).",
        settings.risk_recompute_interval_minutes,
    )
    logger.info(
        "Job de refresh de cohort_xp_standing agendado a cada %d minuto(s).",
        settings.cohort_xp_refresh_interval_minutes,
    )
    logger.info(
        "Job de verificação de lembretes agendado a cada %d minuto(s).",
        settings.reminder_check_interval_minutes,
    )


def shutdown_scheduler() -> None:
    """Encerra o job. Chamado no `lifespan` de shutdown do FastAPI."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
