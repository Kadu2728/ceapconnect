"""Contrato de `GET /admin/journey-os/metrics` (Candidate Journey OS — fase F2)."""

from pydantic import BaseModel, Field


class JourneyOsMetricsResponse(BaseModel):
    """Métricas do Learning Loop: mede se N2 (NBA) e N4 (Modo Resgate) funcionam.

    Taxas `None` = ainda não há denominador suficiente (nenhum NBA gerado
    ou nenhuma entrada em Modo Resgate no período) — nunca `0.0`, que
    esconderia essa diferença.
    """

    window_days: int = Field(description="Janela de tempo considerada, em dias.")
    nba_generated_count: int
    nba_clicked_count: int
    nba_click_through_rate: float | None
    recovery_entered_count: int
    recovery_resumed_count: int
    recovery_resume_rate: float | None
