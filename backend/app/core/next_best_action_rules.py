"""Regras do Next Best Action Engine (Candidate Journey OS — fase N2).

Camada de domínio **pura** (sem I/O): recebe os sinais do Candidate State
(N1) e devolve, no máximo, **uma** ação — nunca uma lista para o candidato
escolher, que é exatamente o problema que o NBA existe para resolver.
Deliberadamente desacoplada de `app.schemas.candidate_state` (mesma
disciplina de `risk_scoring.py`, que também não depende de nenhum schema de
API): quem faz a ponte entre o contrato HTTP e esta regra pura é
`next_best_action_service.py`.

Hoje é uma tabela de decisão por regras. Evoluir para um modelo aprendido
segue a mesma receita já provada em `RiskScorer`: uma segunda implementação
atrás da mesma assinatura, sem tocar no service nem no router.
"""

from dataclasses import dataclass, field
from typing import Final, Literal

from app.core.candidate_state_scoring import MOMENTUM_FLUID, MOMENTUM_STABLE, CandidateMomentum

NextBestActionKey = Literal[
    "upload_documents",
    "remind_guardian",
    "prepare_for_exam",
    "resume_journey",
]

ACTION_UPLOAD_DOCUMENTS: Final = "upload_documents"
ACTION_REMIND_GUARDIAN: Final = "remind_guardian"
ACTION_PREPARE_FOR_EXAM: Final = "prepare_for_exam"
ACTION_RESUME_JOURNEY: Final = "resume_journey"

# A partir de quantos dias até a prova a proximidade em si já justifica a
# recomendação — mesmo limiar de "curto prazo" usado em `ExamCountdown`
# (frontend) para intensificar o tom da contagem regressiva.
_EXAM_PROXIMITY_DAYS: Final = 7

_CTA_LABELS: Final[dict[NextBestActionKey, str]] = {
    ACTION_UPLOAD_DOCUMENTS: "Enviar documentos",
    ACTION_REMIND_GUARDIAN: "Avisar meu responsável",
    ACTION_PREPARE_FOR_EXAM: "Fazer um simulado",
    ACTION_RESUME_JOURNEY: "Continuar minha jornada",
}


@dataclass(frozen=True)
class NextBestActionInput:
    """Só os sinais do Candidate State (N1) que as regras abaixo consultam."""

    momentum: CandidateMomentum
    pending_required_documents: int
    guardian_training_overdue: bool
    days_to_exam: int | None


@dataclass(frozen=True)
class NextBestAction:
    """A ação recomendada, com o "por quê" já em português — nunca uma caixa-preta."""

    action_key: NextBestActionKey
    cta_label: str
    why: list[str] = field(default_factory=list)


def recommend(state: NextBestActionInput) -> NextBestAction | None:
    """A ação com maior potencial de destravar a jornada agora, ou `None`.

    Prioridade, do que mais objetivamente bloqueia o avanço para o que só
    orienta: documento pendente é o gargalo mais citado pela própria
    predição de evasão (`journey_service`, `BLOCKING_STEP_KEYS`);
    responsável atrasado é o fator de maior peso do modelo de risco
    (`_WEIGHT_GUARDIAN_ABSENCE`); proximidade da prova é urgência de tempo;
    retomar a jornada é o fallback para quem está parado sem um bloqueio
    específico identificável. Um candidato "fluid"/"stable" sem nenhum
    desses sinais não recebe recomendação nenhuma — inventar uma quando não
    há nada concreto a dizer violaria o princípio de valor do produto
    (§6 do brief: "se não conseguir responder com clareza, não implemente").
    """
    if state.pending_required_documents > 0:
        return NextBestAction(
            action_key=ACTION_UPLOAD_DOCUMENTS,
            cta_label=_CTA_LABELS[ACTION_UPLOAD_DOCUMENTS],
            why=[_documents_reason(state.pending_required_documents)],
        )

    if state.guardian_training_overdue:
        return NextBestAction(
            action_key=ACTION_REMIND_GUARDIAN,
            cta_label=_CTA_LABELS[ACTION_REMIND_GUARDIAN],
            why=["Seu responsável ainda não confirmou presença na formação obrigatória"],
        )

    if state.days_to_exam is not None and 0 <= state.days_to_exam <= _EXAM_PROXIMITY_DAYS:
        return NextBestAction(
            action_key=ACTION_PREPARE_FOR_EXAM,
            cta_label=_CTA_LABELS[ACTION_PREPARE_FOR_EXAM],
            why=[_exam_reason(state.days_to_exam)],
        )

    if state.momentum not in (MOMENTUM_FLUID, MOMENTUM_STABLE):
        return NextBestAction(
            action_key=ACTION_RESUME_JOURNEY,
            cta_label=_CTA_LABELS[ACTION_RESUME_JOURNEY],
            why=["Sua jornada está parada — vamos continuar de onde você parou"],
        )

    return None


def _documents_reason(pending: int) -> str:
    if pending == 1:
        return "Falta 1 documento para avançar sua jornada"
    return f"Faltam {pending} documentos para avançar sua jornada"


def _exam_reason(days_to_exam: int) -> str:
    if days_to_exam == 0:
        return "Sua prova é hoje"
    if days_to_exam == 1:
        return "Sua prova é amanhã"
    return f"Sua prova é em {days_to_exam} dias"
