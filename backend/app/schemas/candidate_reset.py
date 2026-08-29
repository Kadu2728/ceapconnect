"""Schemas do reset operacional de conta de candidato de teste.

Contrato de `POST /internal/candidates/reset` — nunca exposto por rota
pública, protegido por API key de serviço (mesmo padrão de `/internal/seed`).
"""

from datetime import date

from pydantic import BaseModel, Field


class CandidateResetRequest(BaseModel):
    """Corpo de `POST /internal/candidates/reset`."""

    email: str = Field(min_length=1)
    # Trava deliberada contra chamada acidental — a ação é irreversível
    # (DELETE real em cascata, não soft-delete).
    confirm: bool = Field(
        description="Precisa ser `true` — confirmação explícita de que a ação é irreversível."
    )
    # Contas de responsável criadas só para teste (ex.: durante uma
    # verificação manual do fluxo de consentimento) — removidas por completo,
    # não só desvinculadas. Nunca usado para apagar responsáveis reais.
    also_remove_guardian_emails: list[str] = Field(default_factory=list)


class CandidateResetSummary(BaseModel):
    """Resultado de `POST /internal/candidates/reset`."""

    email: str
    candidate_profile_id: str
    exam_date: date | None
    interview_date: date | None
    guardian_test_accounts_removed: int
