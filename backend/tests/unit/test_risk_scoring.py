"""Testes de `app.core.risk_scoring` (EPIC 14) — primeira cobertura da lógica
mais crítica do produto (decide quem o coordenador vê primeiro no console de
intervenção) e que até aqui não tinha nenhum teste automatizado. Função pura,
sem I/O: não precisa de banco.
"""

from app.core.risk_scoring import (
    TIER_HIGH,
    TIER_LOW,
    TIER_MEDIUM,
    CandidateRiskFeatures,
    HeuristicRiskScorer,
    resolve_tier,
)


def _features(**overrides: object) -> CandidateRiskFeatures:
    """Candidato "saudável" por padrão — cada teste sobrescreve só o que quer variar."""
    base: dict[str, object] = dict(
        candidate_profile_id="11111111-1111-1111-1111-111111111111",
        days_since_last_activity=0.0,
        mission_completion_ratio=1.0,
        missions_abandoned_count=0,
        avg_days_between_completions=None,
        is_stuck_on_blocking_step=False,
        current_step_key="inscricao",
        current_step_label="Inscrição",
        below_cohort_median=False,
        cohort_median_completion_ratio=0.5,
        guardian_has_contact=True,
        guardian_training_attended=True,
        guardian_training_overdue=False,
    )
    base.update(overrides)
    return CandidateRiskFeatures(**base)  # type: ignore[arg-type]


class TestResolveTier:
    def test_baixo_abaixo_de_30(self) -> None:
        assert resolve_tier(0) == TIER_LOW
        assert resolve_tier(29) == TIER_LOW

    def test_medio_entre_30_e_60(self) -> None:
        assert resolve_tier(30) == TIER_MEDIUM
        assert resolve_tier(60) == TIER_MEDIUM

    def test_alto_acima_de_60(self) -> None:
        assert resolve_tier(61) == TIER_HIGH
        assert resolve_tier(100) == TIER_HIGH


class TestHeuristicRiskScorer:
    def setup_method(self) -> None:
        self.scorer = HeuristicRiskScorer()

    def test_candidato_saudavel_tem_score_zero(self) -> None:
        result = self.scorer.score(_features())
        assert result.score == 0
        assert result.tier == TIER_LOW
        assert result.explanation == "Nenhum sinal de risco identificado."

    def test_inatividade_prolongada_aumenta_score(self) -> None:
        result = self.scorer.score(_features(days_since_last_activity=20.0))
        assert result.score > 0
        assert "Sem atividade" in result.explanation

    def test_ausencia_do_responsavel_sozinha_leva_a_risco_alto(self) -> None:
        """Peso 65 (documentado em risk_scoring.py): sozinho, já deve cruzar o
        limiar de 60 e virar tier "alto", sem depender de nenhum outro fator —
        é o comportamento que a mentoria do CEAP pediu explicitamente."""
        # `guardian_training_attended` nunca é True sem contato (ver
        # `risk_feature_service.derive_features_for_group`: só vira True se
        # existir um `Guardian` com `training_attended_at` preenchido) — as
        # duas features andam sempre juntas nos dados reais.
        result = self.scorer.score(
            _features(guardian_has_contact=False, guardian_training_attended=False)
        )
        assert result.tier == TIER_HIGH
        assert result.score >= 60

    def test_responsavel_atrasado_tambem_leva_a_risco_alto(self) -> None:
        result = self.scorer.score(
            _features(
                guardian_has_contact=True,
                guardian_training_attended=False,
                guardian_training_overdue=True,
            )
        )
        assert result.tier == TIER_HIGH

    def test_responsavel_ainda_no_prazo_pesa_menos_que_atrasado(self) -> None:
        no_prazo = self.scorer.score(
            _features(
                guardian_has_contact=True,
                guardian_training_attended=False,
                guardian_training_overdue=False,
            )
        )
        atrasado = self.scorer.score(
            _features(
                guardian_has_contact=True,
                guardian_training_attended=False,
                guardian_training_overdue=True,
            )
        )
        assert no_prazo.score < atrasado.score

    def test_score_nunca_ultrapassa_100(self) -> None:
        result = self.scorer.score(
            _features(
                days_since_last_activity=999.0,
                mission_completion_ratio=0.0,
                missions_abandoned_count=99,
                avg_days_between_completions=999.0,
                is_stuck_on_blocking_step=True,
                below_cohort_median=True,
                guardian_has_contact=False,
                guardian_training_attended=False,
            )
        )
        assert result.score == 100

    def test_explicacao_ordena_fatores_do_maior_para_o_menor(self) -> None:
        result = self.scorer.score(
            _features(days_since_last_activity=20.0, mission_completion_ratio=0.5)
        )
        contributing = [f for f in result.factors if f.points > 0]
        points = [f.points for f in contributing]
        assert points == sorted(points, reverse=True)

    def test_model_version_e_registrado(self) -> None:
        assert self.scorer.model_version == "heuristic-v1"
