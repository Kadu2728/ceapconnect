"""Regra de negócio do funil de conversão da jornada (KPI inscrição→prova).

Fonte: `CandidateProfile.current_journey_step_key`, que desde
`app.services.journey_service` reflete o avanço real do candidato — antes
desta feature, o campo era escrito uma vez no cadastro e nunca mais
atualizado, então não havia dado nenhum para um funil medir.

Como a progressão é sempre sequencial e nunca regride (`journey_service`),
"quantos candidatos alcançaram a etapa N" é a soma de quem está exatamente
nela mais quem já passou dela — nunca uma contagem isolada por etapa atual,
que subestimaria toda etapa anterior à mais avançada de cada candidato.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.funnel_repository import FunnelRepository
from app.repositories.journey_step_repository import JourneyStepRepository
from app.schemas.funnel import FunnelResponse, FunnelStepItem

# Etapa que representa a realização da prova — o destino do KPI que a
# mentoria do CEAP apontou como o gargalo real (inscrição→prova).
_EXAM_DAY_STEP_KEY = "dia_da_prova"


async def get_funnel(db: AsyncSession, *, cohort_ids: list[uuid.UUID] | None) -> FunnelResponse:
    """Monta o funil de conversão. `cohort_ids=None` = irrestrito (admin)."""
    steps = await JourneyStepRepository(db).list_ordered()
    counts_at_order = await FunnelRepository(db).count_by_current_step_order(cohort_ids=cohort_ids)
    total_candidates = sum(counts_at_order.values())

    reached_by_order = {
        step.order: sum(count for order, count in counts_at_order.items() if order >= step.order)
        for step in steps
    }

    items: list[FunnelStepItem] = []
    previous_reached: int | None = None
    for step in steps:
        reached = reached_by_order.get(step.order, 0)
        conversion = (reached / previous_reached) if previous_reached else None
        drop_off = (previous_reached - reached) if previous_reached is not None else None
        items.append(
            FunnelStepItem(
                step_key=step.key,
                label=step.label,
                order=step.order,
                reached=reached,
                conversion_from_previous=conversion,
                drop_off_from_previous=drop_off,
            )
        )
        previous_reached = reached

    exam_day_reached = next(
        (item.reached for item in items if item.step_key == _EXAM_DAY_STEP_KEY), None
    )
    inscricao_to_prova_rate = (
        exam_day_reached / total_candidates
        if exam_day_reached is not None and total_candidates > 0
        else None
    )

    return FunnelResponse(
        steps=items,
        total_candidates=total_candidates,
        inscricao_to_prova_rate=inscricao_to_prova_rate,
    )
