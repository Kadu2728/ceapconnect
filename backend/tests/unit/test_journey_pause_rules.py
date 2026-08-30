"""Testes de `app.core.journey_pause_rules` (Pausa Declarada). Sem I/O."""

from datetime import UTC, date, datetime, timedelta

import pytest

from app.core.journey_pause_rules import (
    EXAM_BUFFER_DAYS,
    PAUSE_OPTION_DAYS,
    PauseTooCloseToExamError,
    is_valid_option,
    resolve_pause_end,
)

_NOW = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)


def test_apenas_os_periodos_oferecidos_sao_validos() -> None:
    for option in PAUSE_OPTION_DAYS:
        assert is_valid_option(option) is True
    # Um período longo transformaria o alívio em hibernação — o freio central.
    assert is_valid_option(30) is False
    assert is_valid_option(0) is False


def test_sem_data_de_prova_a_pausa_dura_o_periodo_pedido() -> None:
    ends_at = resolve_pause_end(started_at=_NOW, requested_days=7, exam_date=None)
    assert ends_at == _NOW + timedelta(days=7)


def test_prova_distante_nao_limita_a_pausa() -> None:
    ends_at = resolve_pause_end(
        started_at=_NOW, requested_days=7, exam_date=(_NOW + timedelta(days=60)).date()
    )
    assert ends_at == _NOW + timedelta(days=7)


def test_prova_proxima_encurta_a_pausa() -> None:
    """O freio que impede a pausa de custar a vaga: 7 dias pedidos, prova em
    5 — a pausa termina com a folga preservada, não em cima da prova."""
    exam_date = (_NOW + timedelta(days=5)).date()

    ends_at = resolve_pause_end(started_at=_NOW, requested_days=7, exam_date=exam_date)

    assert ends_at < _NOW + timedelta(days=7)
    exam_start = datetime.combine(exam_date, datetime.min.time(), tzinfo=UTC)
    assert ends_at <= exam_start - timedelta(days=EXAM_BUFFER_DAYS)


def test_prova_perto_demais_recusa_a_pausa() -> None:
    """Não sobra pausa útil: perto da prova, o que o candidato precisa é aparecer."""
    with pytest.raises(PauseTooCloseToExamError):
        resolve_pause_end(
            started_at=_NOW, requested_days=3, exam_date=(_NOW + timedelta(days=1)).date()
        )


def test_prova_no_passado_recusa_a_pausa() -> None:
    with pytest.raises(PauseTooCloseToExamError):
        resolve_pause_end(started_at=_NOW, requested_days=3, exam_date=date(2026, 1, 1))


def test_fim_da_pausa_sempre_depois_do_inicio() -> None:
    """Invariante que o CHECK `ck_journey_pause_window` também protege no banco."""
    for option in PAUSE_OPTION_DAYS:
        assert resolve_pause_end(started_at=_NOW, requested_days=option, exam_date=None) > _NOW
