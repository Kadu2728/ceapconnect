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

    # --- Pausa Declarada ("Jornada que Respira") ---------------------------
    pause_started_count: int
    #: Voltou clicando "Voltar para minha jornada".
    pause_resumed_count: int
    #: Deixou o prazo passar sem retomar explicitamente.
    pause_expired_count: int
    pause_return_rate: float | None = Field(
        default=None,
        description=(
            "Retomadas explícitas ÷ pausas iniciadas na janela. É a taxa de "
            "**retorno declarado**, não 'seguiu até a prova' — essa exige o "
            "outcome do processo seletivo, que só existe quando ele termina. "
            "Também é descritiva, não causal: sem grupo de controle, não "
            "sustenta afirmação de impacto da mecânica sobre a evasão."
        ),
    )
