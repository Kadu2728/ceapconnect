"""Contrato de `GET /candidate-state` (Candidate Journey OS — N1).

Payload deliberadamente enxuto: só os sinais que N2 (Next Best Action) e N3
(Zero-Click Recovery) precisam para decidir algo, não um segundo agregado de
tela como `DashboardResponse` — quem quer a jornada completa (barra, etapas,
missão, XP) continua usando `GET /dashboard`.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.candidate_state_scoring import CandidateMomentum


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
