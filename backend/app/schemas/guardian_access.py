"""Schemas do RBAC do responsável (conta própria, autenticada).

Contrato de:
- `GET /api/v1/guardian/children`                      → filhos vinculados;
- `GET /api/v1/guardian/children/{id}/journey`          → jornada essencial.

**Nunca** incluir score/tier de risco, texto livre ou qualquer inferência
comportamental — só progresso e pendências concretas (freio de privacidade
do brief). Reaproveita o mesmo formato de `JourneyProgress`/`JourneyStepItem`
do Dashboard do candidato (`app.schemas.dashboard`) porque já é
"progresso puro", sem nada de risco — não há necessidade de um shape novo.
"""

from datetime import date

from pydantic import BaseModel, Field

from app.schemas.dashboard import JourneyProgress


class GuardianLinkChildRequest(BaseModel):
    """Corpo de `POST /guardian/link-children` — responsável já logado
    anexando mais um filho pelo link mágico (ex.: dois irmãos no CEAP)."""

    token: str = Field(min_length=1)


class GuardianChildItem(BaseModel):
    """Um filho vinculado, na lista `GET /guardian/children`."""

    candidate_profile_id: str
    name: str
    current_step_label: str
    journey_percentage: int


class GuardianChildrenResponse(BaseModel):
    children: list[GuardianChildItem]


class GuardianChildJourneyResponse(BaseModel):
    """Jornada essencial de um filho — só o que serve ao acompanhamento."""

    candidate_name: str
    journey: JourneyProgress
    pending_required_documents: int
    exam_date: date | None
    exam_location: str
    interview_date: date | None
    interview_location: str
    guardian_training_date: date | None
    guardian_training_confirmed: bool
    guardian_training_attended: bool
