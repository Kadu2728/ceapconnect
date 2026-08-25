"""Regra de negócio do Learning Loop (Candidate Journey OS — fase F2).

Ponte entre as contagens brutas de `activity_events` e as taxas do
`app.core.journey_os_metrics` — mesmo papel que `risk_service.py`/
`next_best_action_service.py` fazem para suas respectivas camadas puras.

Só mede o que já é emitido de ponta a ponta hoje: `nba_generated`/
`nba_clicked` (N2) e `recovery_entered`/`step_resumed` (N3/N4 — clicar em
"Continuar" no Modo Resgate é o único emissor de `step_resumed` no produto,
então a contagem já vem naturalmente escopada ao fluxo de recuperação).
`nba_completed`/`recovery_completed`/`recovery_exited` seguem reservados no
vocabulário (fase F1) até existir um jeito honesto de detectar conclusão
sem inferir causalidade que a mentoria do CEAP não teria como confirmar.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.journey_os_metrics import safe_rate
from app.models.activity_event import (
    EVENT_NBA_CLICKED,
    EVENT_NBA_GENERATED,
    EVENT_RECOVERY_ENTERED,
    EVENT_STEP_RESUMED,
)
from app.repositories.activity_event_repository import ActivityEventRepository
from app.schemas.journey_os_metrics import JourneyOsMetricsResponse

_DEFAULT_WINDOW_DAYS = 30
_TRACKED_EVENTS = (
    EVENT_NBA_GENERATED,
    EVENT_NBA_CLICKED,
    EVENT_RECOVERY_ENTERED,
    EVENT_STEP_RESUMED,
)


async def get_metrics(
    db: AsyncSession, *, window_days: int = _DEFAULT_WINDOW_DAYS
) -> JourneyOsMetricsResponse:
    since = datetime.now(UTC) - timedelta(days=window_days)
    counts = await ActivityEventRepository(db).count_by_names(list(_TRACKED_EVENTS), since=since)

    nba_generated = counts.get(EVENT_NBA_GENERATED, 0)
    nba_clicked = counts.get(EVENT_NBA_CLICKED, 0)
    recovery_entered = counts.get(EVENT_RECOVERY_ENTERED, 0)
    step_resumed = counts.get(EVENT_STEP_RESUMED, 0)

    return JourneyOsMetricsResponse(
        window_days=window_days,
        nba_generated_count=nba_generated,
        nba_clicked_count=nba_clicked,
        nba_click_through_rate=safe_rate(nba_clicked, nba_generated),
        recovery_entered_count=recovery_entered,
        recovery_resumed_count=step_resumed,
        recovery_resume_rate=safe_rate(step_resumed, recovery_entered),
    )
