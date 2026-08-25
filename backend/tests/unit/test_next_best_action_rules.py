"""Testes de `app.core.next_best_action_rules` (Candidate Journey OS — N2).

Função pura: sem I/O, sem banco. Cobre cada ramo da prioridade e a ordem
entre eles (documento > responsável > prova > jornada parada > nada).
"""

from app.core.candidate_state_scoring import (
    MOMENTUM_FLUID,
    MOMENTUM_FRICTION,
    MOMENTUM_STABLE,
    MOMENTUM_STALLED,
)
from app.core.next_best_action_rules import (
    ACTION_PREPARE_FOR_EXAM,
    ACTION_REMIND_GUARDIAN,
    ACTION_RESUME_JOURNEY,
    ACTION_UPLOAD_DOCUMENTS,
    NextBestActionInput,
    recommend,
)


def _input(**overrides: object) -> NextBestActionInput:
    base: dict[str, object] = dict(
        momentum=MOMENTUM_FLUID,
        pending_required_documents=0,
        guardian_training_overdue=False,
        days_to_exam=None,
    )
    base.update(overrides)
    return NextBestActionInput(**base)  # type: ignore[arg-type]


def test_documento_pendente_e_a_prioridade_mais_alta() -> None:
    action = recommend(
        _input(
            pending_required_documents=1,
            guardian_training_overdue=True,
            days_to_exam=0,
            momentum=MOMENTUM_STALLED,
        )
    )
    assert action is not None
    assert action.action_key == ACTION_UPLOAD_DOCUMENTS
    assert "1 documento" in action.why[0]


def test_documento_pendente_no_plural() -> None:
    action = recommend(_input(pending_required_documents=3))
    assert action is not None
    assert "3 documentos" in action.why[0]


def test_responsavel_atrasado_vence_prova_proxima_e_momentum() -> None:
    action = recommend(
        _input(guardian_training_overdue=True, days_to_exam=1, momentum=MOMENTUM_STALLED)
    )
    assert action is not None
    assert action.action_key == ACTION_REMIND_GUARDIAN


def test_prova_proxima_vence_momentum_parado() -> None:
    action = recommend(_input(days_to_exam=5, momentum=MOMENTUM_STALLED))
    assert action is not None
    assert action.action_key == ACTION_PREPARE_FOR_EXAM


def test_prova_fora_da_janela_de_proximidade_nao_dispara() -> None:
    action = recommend(_input(days_to_exam=30, momentum=MOMENTUM_FLUID))
    assert action is None


def test_momentum_parado_sem_outro_bloqueio_vira_retomar_jornada() -> None:
    for momentum in (MOMENTUM_STALLED, MOMENTUM_FRICTION):
        action = recommend(_input(momentum=momentum))
        assert action is not None
        assert action.action_key == ACTION_RESUME_JOURNEY


def test_candidato_saudavel_nao_recebe_recomendacao() -> None:
    for momentum in (MOMENTUM_FLUID, MOMENTUM_STABLE):
        assert recommend(_input(momentum=momentum)) is None


def test_toda_acao_tem_pelo_menos_um_motivo() -> None:
    cenarios = [
        _input(pending_required_documents=2),
        _input(guardian_training_overdue=True),
        _input(days_to_exam=3),
        _input(momentum=MOMENTUM_STALLED),
    ]
    for cenario in cenarios:
        action = recommend(cenario)
        assert action is not None
        assert len(action.why) >= 1
        assert all(reason.strip() for reason in action.why)
