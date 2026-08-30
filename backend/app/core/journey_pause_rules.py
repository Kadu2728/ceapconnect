"""Regras da Pausa Declarada ("Jornada que Respira" — fase 1).

Camada de domínio **pura** (sem I/O), mesmo espírito de `reminder_rules.py` e
`candidate_state_scoring.py`: recebe dados já resolvidos e devolve a decisão.
Nada aqui lê do banco.

**Por que as opções de período são fechadas e curtas**: a pausa existe para
dar uma saída honesta a "esta semana apertou", não para virar hibernação. Um
campo livre de dias (ou um período longo) transformaria o freio em porta de
saída — exatamente o oposto do objetivo. Duas opções bastam para cobrir o
caso real (o fim de semana que não deu / a semana que virou) sem transformar
uma decisão de alívio numa tela de configuração.
"""

from datetime import UTC, date, datetime, timedelta
from typing import Final, Literal

PauseReasonCode = Literal["trabalho", "tempo", "outro"]

REASON_TRABALHO: Final = "trabalho"
REASON_TEMPO: Final = "tempo"
REASON_OUTRO: Final = "outro"

#: Vocabulário fechado de motivos (CHECK constraint em `journey_pauses`).
#: Deliberadamente genérico e curto: o público inclui menores, e cada
#: categoria a mais é uma inferência a mais sobre a vida de alguém. Nunca
#: existirá texto livre aqui, e nunca haverá uma categoria de saúde (dado
#: sensível — LGPD art. 5º II).
VALID_REASON_CODES: Final = (REASON_TRABALHO, REASON_TEMPO, REASON_OUTRO)

#: Únicos períodos oferecidos, em dias. "Uns dias" e "uma semana".
PAUSE_OPTION_DAYS: Final[tuple[int, ...]] = (3, 7)

#: Folga mínima entre o fim da pausa e a prova. Uma pausa que termina em cima
#: da prova é uma pausa que custa a vaga — o oposto do KPI que o produto
#: existe para proteger.
EXAM_BUFFER_DAYS: Final = 2


class PauseTooCloseToExamError(ValueError):
    """A prova está perto demais para caber qualquer pausa útil."""


def is_valid_option(requested_days: int) -> bool:
    """`True` se o período pedido é uma das opções oferecidas."""
    return requested_days in PAUSE_OPTION_DAYS


def resolve_pause_end(
    *, started_at: datetime, requested_days: int, exam_date: date | None
) -> datetime:
    """Fim efetivo da pausa, já limitado pela proximidade da prova.

    O candidato pede um período; o produto concede `min(pedido, prova −
    folga)`. Guardar os dois valores (`requested_days` e `ends_at`) é o que
    revela depois se estamos oferecendo a pausa tarde demais na jornada — um
    clamp frequente significa que o alívio está chegando quando já não cabe.

    Levanta `PauseTooCloseToExamError` quando nem um dia sobra: perto da
    prova, o que o candidato precisa é aparecer, não pausar.
    """
    natural_end = started_at + timedelta(days=requested_days)
    if exam_date is None:
        return natural_end

    # `exam_date` é uma data pura; a prova acontece ao longo daquele dia, então
    # a folga é contada a partir do início dele.
    exam_start = datetime.combine(exam_date, datetime.min.time(), tzinfo=UTC)
    latest_allowed = exam_start - timedelta(days=EXAM_BUFFER_DAYS)

    if latest_allowed <= started_at:
        raise PauseTooCloseToExamError
    return min(natural_end, latest_allowed)
