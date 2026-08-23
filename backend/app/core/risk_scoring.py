"""Regras de score de evasão (EPIC 14 — Predição de evasão).

Camada de domínio **pura** (sem I/O), no mesmo espírito de `gamification.py`:
recebe features já derivadas e devolve um score explicável. Nada aqui lê do
banco — quem monta `CandidateRiskFeatures` é `risk_feature_service.py`.

**Princípio de engenharia:** o cálculo do score vive atrás da interface
`RiskScorer`. Hoje só existe `HeuristicRiskScorer` (soma ponderada, cada fator
com um motivo em português). Trocar por um modelo treinado (ex.: regressão
logística) no futuro significa escrever uma nova classe que implementa
`RiskScorer` e injetá-la em `risk_service.py` — nenhuma outra camada muda.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Final, Literal

RiskTier = Literal["baixo", "medio", "alto"]

TIER_LOW: Final = "baixo"
TIER_MEDIUM: Final = "medio"
TIER_HIGH: Final = "alto"

# Limiares de tier (spec): baixo <30 / médio 30–60 / alto >60.
_TIER_MEDIUM_MIN: Final = 30
_TIER_HIGH_MIN: Final = 60


def resolve_tier(score: int) -> RiskTier:
    """Converte um score (0–100) no tier correspondente."""
    if score > _TIER_HIGH_MIN:
        return TIER_HIGH
    if score >= _TIER_MEDIUM_MIN:
        return TIER_MEDIUM
    return TIER_LOW


@dataclass(frozen=True)
class CandidateRiskFeatures:
    """Features derivadas do comportamento de um candidato (fase 3, input do score).

    Tudo aqui é o resultado de uma leitura de `activity_events` + progresso —
    ver `risk_feature_service.py`. Nenhum campo é calculado nesta classe.
    """

    candidate_profile_id: str
    # Dias desde o último sinal de atividade. Se o candidato nunca teve
    # nenhum `ActivityEvent`, o "último sinal" é a data de cadastro — assim um
    # candidato recém-inscrito começa com risco baixo (ainda não teve tempo de
    # agir), em vez de ser tratado como pior caso só por falta de dado.
    days_since_last_activity: float
    # 0..1 — missões concluídas / total de missões do catálogo.
    mission_completion_ratio: float
    missions_abandoned_count: int
    # Média de dias entre conclusões consecutivas de missão. None = menos de
    # 2 conclusões (dado insuficiente para medir ritmo).
    avg_days_between_completions: float | None
    is_stuck_on_blocking_step: bool
    current_step_key: str
    current_step_label: str
    # None = coorte sem dado suficiente para mediana (ex.: 1 único candidato).
    below_cohort_median: bool | None
    cohort_median_completion_ratio: float | None
    # Responsável (mentoria do CEAP: fator de evasão de primeira ordem — se
    # não participa da formação obrigatória, o candidato perde a vaga).
    # `guardian_has_contact=False` = nenhum responsável cadastrado ainda.
    guardian_has_contact: bool
    guardian_training_attended: bool
    # `True` = a data da formação da coorte já passou e o responsável não
    # compareceu. `False` também quando não há data definida (sem prazo
    # vencido, sem risco de atraso a apontar).
    guardian_training_overdue: bool


@dataclass(frozen=True)
class RiskFactor:
    """Um fator que contribuiu para o score, com o motivo em linguagem humana."""

    key: str
    label: str
    points: float


@dataclass(frozen=True)
class RiskScoreResult:
    """Resultado do cálculo: score, tier e a explicação decomponível em fatores."""

    score: int
    tier: RiskTier
    factors: list[RiskFactor] = field(default_factory=list)

    @property
    def explanation(self) -> str:
        """Texto humano pronto para UI (ex.: "Sem atividade há 5 dias · ...").

        Junta só os fatores que de fato contribuíram (`points > 0`), do maior
        para o menor — os motivos mais fortes aparecem primeiro.
        """
        contributing = sorted(
            (f for f in self.factors if f.points > 0), key=lambda f: f.points, reverse=True
        )
        if not contributing:
            return "Nenhum sinal de risco identificado."
        return " · ".join(f.label for f in contributing)


class RiskScorer(ABC):
    """Interface abstrata do cálculo de score de evasão.

    Qualquer implementação (heurística hoje, um modelo treinado amanhã) recebe
    `CandidateRiskFeatures` e devolve `RiskScoreResult`. `risk_service.py`
    depende apenas desta interface — nunca de `HeuristicRiskScorer`
    diretamente — para a troca de modelo não exigir reescrever o resto do
    sistema.
    """

    #: Identificador da versão do modelo (ex.: "heuristic-v1"). Toda
    #: implementação concreta define o seu — é gravado em cada `RiskScore` e
    #: `RiskScoreHistory` calculado, para o harness de backtest saber qual
    #: modelo gerou qual score.
    model_version: str

    @abstractmethod
    def score(self, features: CandidateRiskFeatures) -> RiskScoreResult:
        """Calcula o score de risco (0–100) e os fatores que o explicam."""
        raise NotImplementedError


# --- Pesos da heurística ------------------------------------------------
#
# Cada peso é o teto de contribuição daquele fator; a fórmula de cada um
# decide quanto do teto é efetivamente atingido. Ajustar estes números (ou a
# fórmula de cada `_score_*`) NUNCA exige mudar `risk_service.py` ou os
# endpoints — é a vantagem de manter tudo atrás de `RiskScorer`.
#
# Os 6 primeiros somam exatamente 100 (o orçamento original do modelo).
# `_WEIGHT_GUARDIAN_ABSENCE` foi somado por cima, de propósito: a mentoria do
# CEAP identificou a ausência do responsável na formação obrigatória como
# quase-determinística para perda de vaga — sozinho, esse fator já deve levar
# o candidato a risco "alto" (>60), sem depender de nenhum outro sinal.
# `score()` clampa o total em 100 de qualquer forma, então isso nunca gera um
# score fora de faixa — só garante que este sinal nunca fica diluído entre os
# outros seis.
_WEIGHT_INACTIVITY: Final = 35.0
_WEIGHT_LOW_COMPLETION: Final = 20.0
_WEIGHT_ABANDONED_MISSIONS: Final = 15.0
_WEIGHT_STUCK_STEP: Final = 15.0
_WEIGHT_BELOW_COHORT_MEDIAN: Final = 10.0
_WEIGHT_SLOW_PACE: Final = 5.0
_WEIGHT_GUARDIAN_ABSENCE: Final = 65.0

# Dias de tolerância antes da inatividade começar a pontuar.
_INACTIVITY_GRACE_DAYS: Final = 2.0
# Pontos por dia de inatividade após a tolerância.
_INACTIVITY_POINTS_PER_DAY: Final = 3.5

# Ritmo esperado entre conclusões de missão; acima disso, cada dia extra soma
# ao fator "ritmo lento".
_EXPECTED_PACE_DAYS: Final = 5.0
_SLOW_PACE_POINTS_PER_DAY: Final = 1.0


class HeuristicRiskScorer(RiskScorer):
    """Score = soma ponderada e explicável de sinais comportamentais.

    Cada `_score_*` calcula a contribuição (0..peso máximo) de um único sinal
    e produz o `RiskFactor` com o texto que justifica aquele pedaço do score —
    é assim que o sistema sempre consegue dizer "por que" um candidato está em
    risco, em vez de devolver um número opaco.
    """

    model_version: Final = "heuristic-v1"

    def score(self, features: CandidateRiskFeatures) -> RiskScoreResult:
        factors = [
            self._score_inactivity(features),
            self._score_low_completion(features),
            self._score_abandoned_missions(features),
            self._score_stuck_step(features),
            self._score_below_cohort_median(features),
            self._score_slow_pace(features),
            self._score_guardian_absence(features),
        ]
        raw_score = sum(f.points for f in factors)
        score = round(min(100.0, max(0.0, raw_score)))
        return RiskScoreResult(score=score, tier=resolve_tier(score), factors=factors)

    def _score_inactivity(self, f: CandidateRiskFeatures) -> RiskFactor:
        days = f.days_since_last_activity
        points = min(
            _WEIGHT_INACTIVITY,
            max(0.0, (days - _INACTIVITY_GRACE_DAYS) * _INACTIVITY_POINTS_PER_DAY),
        )
        days_rounded = round(days)
        label = f"Sem atividade há {days_rounded} dia(s)" if points > 0 else "Ativo recentemente"
        return RiskFactor("inactivity", label, points)

    def _score_low_completion(self, f: CandidateRiskFeatures) -> RiskFactor:
        points = (1 - f.mission_completion_ratio) * _WEIGHT_LOW_COMPLETION
        pct = round(f.mission_completion_ratio * 100)
        return RiskFactor("low_completion", f"{pct}% das missões concluídas", points)

    def _score_abandoned_missions(self, f: CandidateRiskFeatures) -> RiskFactor:
        count = f.missions_abandoned_count
        points = min(_WEIGHT_ABANDONED_MISSIONS, count * (_WEIGHT_ABANDONED_MISSIONS / 2))
        label = f"{count} missão(ões) abandonada(s)" if count > 0 else "Nenhuma missão abandonada"
        return RiskFactor("abandoned_missions", label, points)

    def _score_stuck_step(self, f: CandidateRiskFeatures) -> RiskFactor:
        points = _WEIGHT_STUCK_STEP if f.is_stuck_on_blocking_step else 0.0
        label = f"Travado em {f.current_step_label}" if f.is_stuck_on_blocking_step else ""
        return RiskFactor("stuck_step", label, points)

    def _score_below_cohort_median(self, f: CandidateRiskFeatures) -> RiskFactor:
        points = _WEIGHT_BELOW_COHORT_MEDIAN if f.below_cohort_median else 0.0
        label = "Progresso abaixo da média da turma" if f.below_cohort_median else ""
        return RiskFactor("below_cohort_median", label, points)

    def _score_slow_pace(self, f: CandidateRiskFeatures) -> RiskFactor:
        avg = f.avg_days_between_completions
        if avg is None or avg <= _EXPECTED_PACE_DAYS:
            return RiskFactor("slow_pace", "", 0.0)
        points = min(_WEIGHT_SLOW_PACE, (avg - _EXPECTED_PACE_DAYS) * _SLOW_PACE_POINTS_PER_DAY)
        return RiskFactor("slow_pace", f"Ritmo lento (a cada {round(avg)} dias)", points)

    def _score_guardian_absence(self, f: CandidateRiskFeatures) -> RiskFactor:
        if f.guardian_training_attended:
            return RiskFactor(
                "guardian_absence", "Responsável concluiu a formação obrigatória", 0.0
            )
        if not f.guardian_has_contact:
            return RiskFactor(
                "guardian_absence",
                "Nenhum responsável cadastrado — formação obrigatória em risco",
                _WEIGHT_GUARDIAN_ABSENCE,
            )
        if f.guardian_training_overdue:
            return RiskFactor(
                "guardian_absence",
                "Responsável não compareceu à formação obrigatória (perda de vaga iminente)",
                _WEIGHT_GUARDIAN_ABSENCE,
            )
        return RiskFactor(
            "guardian_absence",
            "Responsável ainda não concluiu a formação obrigatória",
            _WEIGHT_GUARDIAN_ABSENCE * 0.25,
        )
