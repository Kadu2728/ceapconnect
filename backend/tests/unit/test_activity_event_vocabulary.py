"""Testes de `app.models.activity_event` (Candidate Journey OS — fase F1).

Garante que o `Literal` de tipo (`ActivityEventName`, checado estaticamente
pelo mypy/type-checker) e a tupla usada na `CHECK CONSTRAINT` em runtime
nunca divirjam — os dois são escritos à mão, lado a lado, e nada além de
disciplina manual os mantém sincronizados hoje.
"""

import typing

from app.models import activity_event as ae


def test_constantes_de_evento_batem_com_a_tupla_valida() -> None:
    all_constants = {
        value
        for name, value in vars(ae).items()
        if name.startswith("EVENT_") and isinstance(value, str)
    }
    assert all_constants == set(ae._VALID_EVENT_NAMES)  # noqa: SLF001 — teste da própria constante


def test_literal_type_bate_com_a_tupla_valida() -> None:
    literal_args = set(typing.get_args(ae.ActivityEventName))
    assert literal_args == set(ae._VALID_EVENT_NAMES)  # noqa: SLF001


def test_vocabulario_do_candidate_journey_os_esta_presente() -> None:
    """As 8 adições da fase F1 — se uma sumir por engano, N2/N3/N4 quebram
    silenciosamente (o `track()` engoliria a exceção do CHECK constraint,
    ver `activity_event_service` — best-effort por design)."""
    novos = {
        ae.EVENT_STEP_ABANDONED,
        ae.EVENT_STEP_RESUMED,
        ae.EVENT_NBA_GENERATED,
        ae.EVENT_NBA_CLICKED,
        ae.EVENT_NBA_COMPLETED,
        ae.EVENT_RECOVERY_ENTERED,
        ae.EVENT_RECOVERY_COMPLETED,
        ae.EVENT_RECOVERY_EXITED,
    }
    assert novos.issubset(set(ae._VALID_EVENT_NAMES))  # noqa: SLF001
    assert len(novos) == 8
