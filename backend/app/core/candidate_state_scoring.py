"""Classificação de momentum do Candidate State (Candidate Journey OS — N1).

Camada de domínio **pura** (sem I/O), no mesmo espírito de `risk_scoring.py`:
recebe features já derivadas e devolve um estado. Nada aqui lê do banco —
`candidate_state_service.py` reaproveita `risk_feature_service.py` (o mesmo
derivador de sinais do motor de risco) para montar o input, em vez de ler o
mesmo dado do banco de uma segunda forma.

**Por que reaproveitar `CandidateRiskFeatures` em vez de um dataclass novo**:
o risco de evasão e o momentum da jornada respondem à mesma pergunta —
"como este candidato está indo?" — só que em resoluções diferentes (score
0-100 para o coordenador agir; um estado qualitativo para a experiência se
adaptar). Ter duas derivações de sinal independentes para a mesma pergunta
criaria a possibilidade real de "por que meu risco diz X mas minha
experiência age como Y" — o tipo de inconsistência que a auditoria de
arquitetura already sinalizou como risco a evitar.

**Por que não é um score contínuo**: o brief do produto é explícito —
"mecanismo de decisão, NÃO exibido como score assustador ao candidato". Um
enum de 5 valores não tem a mesma superfície de "número que parece
sentença" que um score teria, e ainda assim é suficiente para todo o
consumo que N2 (Next Best Action) e N4 (Modo Resgate) precisam fazer:
ramificar comportamento, não medir precisão.
"""

from typing import Final, Literal

from app.core.risk_scoring import CandidateRiskFeatures

CandidateMomentum = Literal["fluid", "stable", "friction", "stalled", "recovery"]

MOMENTUM_FLUID: Final = "fluid"
MOMENTUM_STABLE: Final = "stable"
MOMENTUM_FRICTION: Final = "friction"
MOMENTUM_STALLED: Final = "stalled"
MOMENTUM_RECOVERY: Final = "recovery"

#: Versão da lógica de classificação — vai em `CandidateStateResponse.version`
#: (mesma disciplina de `RiskScorer.model_version`), para o Learning Loop (F2)
#: conseguir distinguir "mudou o comportamento do candidato" de "mudamos a
#: régua que decide o estado dele".
STATE_VERSION: Final = "v1"

# Dias de inatividade a partir dos quais o candidato é considerado parado —
# o sinal mais forte e menos ambíguo que existe (ninguém interpreta mal
# "sumiu há uma semana").
_STALLED_INACTIVITY_DAYS: Final = 7.0
# Dias de inatividade que já configuram fricção, mesmo sem outro sinal.
_FRICTION_INACTIVITY_DAYS: Final = 3.0
# Janela de retorno: atividade dentro desse número de dias conta como
# "acabou de voltar", não como "sempre esteve ativo".
_RECOVERY_WINDOW_DAYS: Final = 1.0
# Duas missões abandonadas já é padrão, não acidente isolado.
_FRICTION_ABANDONED_THRESHOLD: Final = 2


def classify_momentum(features: CandidateRiskFeatures) -> CandidateMomentum:
    """Deriva o estado qualitativo da jornada a partir das mesmas features do risco.

    Avaliação em ordem — a primeira regra que bate decide, do sinal mais
    forte (silêncio prolongado) para o mais fraco (nada de anormal). Isso
    torna os ramos mutuamente exclusivos por construção, sem precisar de
    `elif` explícito nem risco de dois ramos baterem ao mesmo tempo.
    """
    has_friction_markers = (
        features.is_stuck_on_blocking_step or features.missions_abandoned_count >= 1
    )

    if features.days_since_last_activity >= _STALLED_INACTIVITY_DAYS:
        return MOMENTUM_STALLED

    if features.days_since_last_activity <= _RECOVERY_WINDOW_DAYS and has_friction_markers:
        # Voltou recentemente, mas ainda carrega o motivo que o afastou —
        # o momento exato em que uma retomada gentil (N3/N4) importa mais.
        return MOMENTUM_RECOVERY

    if (
        features.is_stuck_on_blocking_step
        or features.missions_abandoned_count >= _FRICTION_ABANDONED_THRESHOLD
        or features.days_since_last_activity >= _FRICTION_INACTIVITY_DAYS
    ):
        return MOMENTUM_FRICTION

    if (
        features.days_since_last_activity <= _RECOVERY_WINDOW_DAYS
        and features.missions_abandoned_count == 0
    ):
        return MOMENTUM_FLUID

    return MOMENTUM_STABLE
