"""Testes de `app.core.candidate_state_scoring` (Candidate Journey OS — N1).

Função pura: recebe `CandidateRiskFeatures` (o mesmo tipo que alimenta o
motor de risco) e devolve um `CandidateMomentum`. Sem I/O, sem banco.
"""

from app.core.candidate_state_scoring import (
    MOMENTUM_FLUID,
    MOMENTUM_FRICTION,
    MOMENTUM_RECOVERY,
    MOMENTUM_STABLE,
    MOMENTUM_STALLED,
    classify_momentum,
)
from app.core.risk_scoring import CandidateRiskFeatures


def _features(**overrides: object) -> CandidateRiskFeatures:
    base: dict[str, object] = dict(
        candidate_profile_id="11111111-1111-1111-1111-111111111111",
        days_since_last_activity=0.0,
        mission_completion_ratio=0.5,
        missions_abandoned_count=0,
        avg_days_between_completions=None,
        is_stuck_on_blocking_step=False,
        current_step_key="documentacao",
        current_step_label="Documentação",
        below_cohort_median=False,
        cohort_median_completion_ratio=0.5,
        guardian_has_contact=True,
        guardian_training_attended=True,
        guardian_training_overdue=False,
    )
    base.update(overrides)
    return CandidateRiskFeatures(**base)  # type: ignore[arg-type]


def test_inatividade_de_uma_semana_ou_mais_e_stalled() -> None:
    assert classify_momentum(_features(days_since_last_activity=7.0)) == MOMENTUM_STALLED
    assert classify_momentum(_features(days_since_last_activity=30.0)) == MOMENTUM_STALLED


def test_stalled_vence_mesmo_com_sinais_de_friccao_junto() -> None:
    """Silêncio prolongado é o sinal mais forte — não importa o que mais aconteceu."""
    result = classify_momentum(
        _features(days_since_last_activity=10.0, is_stuck_on_blocking_step=True)
    )
    assert result == MOMENTUM_STALLED


def test_retorno_recente_com_fricção_anterior_e_recovery() -> None:
    result = classify_momentum(_features(days_since_last_activity=0.5, missions_abandoned_count=1))
    assert result == MOMENTUM_RECOVERY


def test_retorno_recente_travado_em_etapa_bloqueante_e_recovery() -> None:
    result = classify_momentum(
        _features(days_since_last_activity=0.0, is_stuck_on_blocking_step=True)
    )
    assert result == MOMENTUM_RECOVERY


def test_travado_em_etapa_bloqueante_sem_ser_retorno_recente_e_friction() -> None:
    result = classify_momentum(
        _features(days_since_last_activity=5.0, is_stuck_on_blocking_step=True)
    )
    assert result == MOMENTUM_FRICTION


def test_duas_ou_mais_missoes_abandonadas_e_friction() -> None:
    result = classify_momentum(_features(days_since_last_activity=2.0, missions_abandoned_count=2))
    assert result == MOMENTUM_FRICTION


def test_inatividade_de_tres_dias_sem_outro_sinal_e_friction() -> None:
    result = classify_momentum(_features(days_since_last_activity=3.0))
    assert result == MOMENTUM_FRICTION


def test_ativo_agora_sem_nenhuma_fricção_e_fluid() -> None:
    result = classify_momentum(_features(days_since_last_activity=0.0, missions_abandoned_count=0))
    assert result == MOMENTUM_FLUID


def test_atividade_ha_dois_dias_sem_fricção_e_stable() -> None:
    """Nem parado, nem "acabou de agir agora", nem em fricção clara: o meio-termo."""
    result = classify_momentum(_features(days_since_last_activity=2.0, missions_abandoned_count=0))
    assert result == MOMENTUM_STABLE


def test_estados_sao_mutuamente_exclusivos_em_uma_varredura() -> None:
    """Amostra ampla de combinações — cada uma deve cair em exatamente um estado
    (a função sempre retorna um único valor, então isto garante que nenhuma
    combinação testada levanta exceção nem produz algo fora do enum)."""
    valid_states = {
        MOMENTUM_FLUID,
        MOMENTUM_STABLE,
        MOMENTUM_FRICTION,
        MOMENTUM_STALLED,
        MOMENTUM_RECOVERY,
    }
    for days in (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 15.0):
        for abandoned in (0, 1, 2, 5):
            for stuck in (False, True):
                result = classify_momentum(
                    _features(
                        days_since_last_activity=days,
                        missions_abandoned_count=abandoned,
                        is_stuck_on_blocking_step=stuck,
                    )
                )
                assert result in valid_states
