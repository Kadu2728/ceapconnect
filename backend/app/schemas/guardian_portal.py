"""Schemas do Portal do Responsável (link mágico, sem conta/login).

Contrato de:
- `GET  /api/v1/guardian-portal/{token}`         → dados para a tela de confirmação;
- `POST /api/v1/guardian-portal/{token}/confirm` → confirma presença na formação.

Deliberadamente enxuto: só o que o responsável precisa ver para decidir e
confirmar — nunca o nome completo/CPF do candidato, nunca o score de risco,
nunca dados de outros candidatos.
"""

from datetime import date, datetime

from pydantic import BaseModel


class GuardianPortalView(BaseModel):
    """O que o responsável vê na tela de confirmação."""

    candidate_first_name: str
    training_date: date | None
    training_location: str
    training_confirmed_at: datetime | None
    training_attended_at: datetime | None
