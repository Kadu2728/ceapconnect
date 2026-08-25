"""Contrato de `GET /next-best-action` (Candidate Journey OS — fase N2)."""

from pydantic import BaseModel

from app.core.next_best_action_rules import NextBestActionKey


class NextBestActionResponse(BaseModel):
    """A ação única recomendada ao candidato agora, com o motivo em português."""

    action_key: NextBestActionKey
    cta_label: str
    why: list[str]
