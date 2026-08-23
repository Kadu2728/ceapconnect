"""Schemas do responsável — alvo duplo no Console de Intervenção e Área de Pais.

Contrato de:
- `GET   /api/v1/admin/guardians/at-risk`                 → famílias que precisam de atenção;
- `POST  /api/v1/admin/guardians/interventions`            → registra um contato;
- `POST  /api/v1/admin/guardians/{id}/training-confirmed`  → confirma presença;
- `POST  /api/v1/admin/guardians/{id}/training-attended`   → marca presença na formação;
- `PATCH /api/v1/admin/cohorts/{id}/guardian-training-date` → data da formação da coorte.

Mesma regra do Console de candidatos: nada aqui é exposto a candidatos, só a
coordenador/admin sob `CohortScope`.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.intervention import InterventionChannel, InterventionOutcome


class GuardianAtRiskItem(BaseModel):
    """Uma família (candidato + responsável, se cadastrado) que precisa de atenção."""

    candidate_profile_id: uuid.UUID
    candidate_name: str
    candidate_email: str
    cohort_id: uuid.UUID | None
    cohort_name: str | None
    # None = nenhum responsável cadastrado ainda — a ação é contatar o
    # CANDIDATO (via /admin/interventions), não o responsável.
    guardian_id: uuid.UUID | None
    guardian_name: str | None
    guardian_phone: str | None
    guardian_email: str | None
    training_confirmed_at: datetime | None
    training_attended_at: datetime | None
    guardian_training_date: date | None
    reason: str


class GuardiansAtRiskResponse(BaseModel):
    """Payload de `GET /api/v1/admin/guardians/at-risk`."""

    items: list[GuardianAtRiskItem]
    total: int


class GuardianInterventionCreateRequest(BaseModel):
    """Corpo de `POST /api/v1/admin/guardians/interventions`."""

    guardian_id: uuid.UUID
    channel: InterventionChannel
    outcome: InterventionOutcome
    notes: str | None = Field(default=None, max_length=1000)


class GuardianInterventionItem(BaseModel):
    """Uma intervenção registrada com um responsável."""

    id: uuid.UUID
    channel: InterventionChannel
    outcome: InterventionOutcome
    notes: str | None
    created_by_name: str | None
    created_at: datetime


class GuardianMilestoneItem(BaseModel):
    """Payload de `POST .../training-confirmed` e `.../training-attended`."""

    guardian_id: uuid.UUID
    training_confirmed_at: datetime | None
    training_attended_at: datetime | None


class CohortTrainingDateUpdateRequest(BaseModel):
    """Corpo de `PATCH /api/v1/admin/cohorts/{id}/guardian-training-date`."""

    guardian_training_date: date | None
