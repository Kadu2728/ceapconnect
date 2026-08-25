"""Testes de `app.core.journey_os_metrics` (Candidate Journey OS — F2).

Função pura: sem I/O, sem banco.
"""

from app.core.journey_os_metrics import safe_rate


def test_divide_normalmente_quando_ha_denominador() -> None:
    assert safe_rate(1, 4) == 0.25
    assert safe_rate(0, 4) == 0.0
    assert safe_rate(4, 4) == 1.0


def test_denominador_zero_e_none_nao_zero() -> None:
    """`0.0` significaria "gerou NBA e ninguém clicou" — um estado bem
    diferente de "nenhum NBA foi gerado ainda"; misturar os dois enganaria
    quem lê a métrica."""
    assert safe_rate(0, 0) is None
