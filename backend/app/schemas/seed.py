"""Contrato de `POST /internal/seed`."""

from pydantic import BaseModel


class SeedSummary(BaseModel):
    """Quantos registros cada catálogo ganhou nesta execução do seed.

    Sempre 0 num catálogo já semeado antes — rodar de novo em produção
    nunca duplica, só preenche o que for novo (ex.: questões de simulado
    adicionadas depois do primeiro deploy).
    """

    journey_steps_created: int
    missions_created: int
    achievements_created: int
    events_created: int
    rewards_created: int
    cohorts_created: int
    profiles_assigned_to_cohort: int
    simulado_questions_created: int
