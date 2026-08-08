"""Schemas Pydantic dos Simulados de prova (EPIC 16).

Contrato de:
- `POST /api/v1/simulados/start`                  → sorteia as questões, abre a tentativa;
- `POST /api/v1/simulados/{attempt_id}/answer`    → responde 1 questão, feedback imediato;
- `POST /api/v1/simulados/{attempt_id}/finish`    → fecha a tentativa, devolve o resultado;
- `GET  /api/v1/simulados/history`                → histórico de tentativas do candidato.

**Nunca** expor `correct_option_key`/`explanation` no schema de questão usado
durante a tentativa (`SimuladoQuestionPublic`) — vazaria a resposta antes do
candidato responder. Só aparecem em `AnswerResult`, após a resposta ser dada.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.simulado import SimuladoSubject


class QuestionOption(BaseModel):
    key: str
    text: str


class SimuladoQuestionPublic(BaseModel):
    """Uma questão como é exibida durante a tentativa — sem a resposta certa."""

    id: uuid.UUID
    subject: SimuladoSubject
    statement: str
    options: list[QuestionOption]


class StartAttemptResponse(BaseModel):
    """Payload de `POST /api/v1/simulados/start`."""

    attempt_id: uuid.UUID
    questions: list[SimuladoQuestionPublic]


class AnswerRequest(BaseModel):
    """Corpo de `POST /api/v1/simulados/{attempt_id}/answer`."""

    question_id: uuid.UUID
    selected_option_key: str


class AnswerResult(BaseModel):
    """Payload de resposta — feedback imediato, o valor pedagógico do simulado."""

    question_id: uuid.UUID
    is_correct: bool
    correct_option_key: str
    explanation: str


class SubjectBreakdown(BaseModel):
    subject: SimuladoSubject
    correct: int
    total: int


class FinishAttemptResponse(BaseModel):
    """Payload de `POST /api/v1/simulados/{attempt_id}/finish`."""

    attempt_id: uuid.UUID
    correct_count: int
    total_questions: int
    score_percentage: int
    subject_breakdown: list[SubjectBreakdown]
    xp_awarded: int


class AttemptHistoryItem(BaseModel):
    """Um item do histórico de simulados do candidato."""

    attempt_id: uuid.UUID
    finished_at: datetime
    correct_count: int
    total_questions: int
    score_percentage: int


class AttemptHistoryResponse(BaseModel):
    """Payload de `GET /api/v1/simulados/history`."""

    attempts: list[AttemptHistoryItem]
    best_score_percentage: int | None
