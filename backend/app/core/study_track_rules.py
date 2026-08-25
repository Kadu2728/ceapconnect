"""Regra da trilha de estudo: qual matéria merece mais atenção agora.

Camada de domínio **pura** (sem I/O): recebe a contagem de acertos/total por
matéria — já calculada por `SimuladoAnswerRepository.subject_breakdown_*` —
e devolve a mais fraca, ou `None` quando o dado ainda não sustenta uma
recomendação com confiança (menos de 2 matérias respondidas, ou empate
exato entre elas). O simulado hoje só tem 2 matérias (Português/Matemática),
mas a regra é escrita para qualquer número, sem hardcode.
"""

from typing import Final

_MIN_SUBJECTS_TO_COMPARE: Final = 2


def resolve_weakest_subject(breakdown: list[tuple[str, int, int]]) -> str | None:
    """A matéria com menor taxa de acerto entre as informadas, ou `None`.

    `breakdown`: lista de `(subject, correct, total)`. Matérias com
    `total == 0` (nenhuma questão respondida) são ignoradas — não há taxa de
    acerto para comparar.
    """
    scored = [(subject, correct / total) for subject, correct, total in breakdown if total > 0]
    if len(scored) < _MIN_SUBJECTS_TO_COMPARE:
        return None

    scored.sort(key=lambda item: item[1])
    lowest_subject, lowest_ratio = scored[0]
    if all(ratio == lowest_ratio for _, ratio in scored):
        return None
    return lowest_subject
