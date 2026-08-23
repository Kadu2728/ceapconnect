"""Schemas do funil de conversão da jornada (KPI inscrição→prova).

Contrato de `GET /api/v1/admin/funnel`.
"""

from pydantic import BaseModel


class FunnelStepItem(BaseModel):
    """Uma etapa do funil: quantos candidatos já a alcançaram e a queda desde a anterior."""

    step_key: str
    label: str
    order: int
    # Candidatos que já alcançaram esta etapa (nela ou além — a jornada nunca
    # regride, ver `app.services.journey_service`).
    reached: int
    # `None` na 1ª etapa (não há "anterior" pra comparar).
    conversion_from_previous: float | None
    drop_off_from_previous: int | None


class FunnelResponse(BaseModel):
    """Payload de `GET /api/v1/admin/funnel`."""

    steps: list[FunnelStepItem]
    total_candidates: int
    # Destaque do KPI: a mentoria do CEAP identificou este trecho — não o
    # funil inteiro — como o gargalo real da conversão.
    inscricao_to_prova_rate: float | None
