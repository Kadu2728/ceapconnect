"""Contrato de `GET /candidate-state` (Candidate Journey OS — N1).

Payload deliberadamente enxuto: só os sinais que N2 (Next Best Action) e N3
(Zero-Click Recovery) precisam para decidir algo, não um segundo agregado de
tela como `DashboardResponse` — quem quer a jornada completa (barra, etapas,
missão, XP) continua usando `GET /dashboard`.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.candidate_state_scoring import CandidateMomentum
from app.schemas.journey_pause import PauseState

#: Subconjunto do vocabulário de `app.models.activity_event` que o próprio
#: candidato pode disparar client-side (cliques, entrada/saída de modo).
#: Deliberadamente NÃO inclui eventos que já têm um fluxo de servidor
#: autoritativo (`step_completed`, `document_uploaded`, `mission_completed`,
#: `nba_generated`...) — um endpoint genérico não pode virar porta para o
#: candidato "declarar" um evento que deveria vir de uma ação real no
#: backend.
CandidateTrackableEvent = Literal[
    "nba_clicked",
    "step_resumed",
    "recovery_entered",
    "recovery_completed",
    "recovery_exited",
]


class TrackEventRequest(BaseModel):
    """Corpo de `POST /candidate-state/events`."""

    name: CandidateTrackableEvent
    props: dict[str, Any] = Field(default_factory=dict)


class CandidateStateResponse(BaseModel):
    """Estado computado da jornada do candidato autenticado.

    `momentum` é o mecanismo de decisão do produto (gate do Modo Resgate,
    input do Next Best Action) — nunca deve ser renderizado como texto cru
    na interface do candidato (ver PROJECT_OVERVIEW.md/ARCHITECTURE.md:
    o candidato nunca vê seu próprio risco em número; o mesmo princípio vale
    aqui para o estado qualitativo).
    """

    version: str = Field(description="Versão da lógica de classificação (STATE_VERSION).")
    computed_at: datetime
    momentum: CandidateMomentum
    current_step_key: str
    days_since_last_activity: float
    pending_required_documents: int = Field(
        description="Quantos dos documentos obrigatórios ainda faltam ser enviados."
    )
    days_to_exam: int | None = Field(
        default=None, description="Dias até a prova. `None` se `exam_date` não estiver definida."
    )
    guardian_training_overdue: bool
    pause: PauseState | None = Field(
        default=None,
        description=(
            "Pausa declarada em curso, ou `None`. Quando presente, tem "
            "precedência sobre `momentum`: a experiência para de cobrar avanço "
            "(sem Next Best Action, sem Modo Resgate)."
        ),
    )
