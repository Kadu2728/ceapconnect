"""Cálculo de taxas do Learning Loop (Candidate Journey OS — fase F2).

Camada de domínio **pura**: recebe contagens já agregadas por
`ActivityEventRepository.count_by_names` e devolve as taxas prontas para o
schema de resposta. Nenhuma query mora aqui — mesma separação de
`risk_scoring.py`/`next_best_action_rules.py`.
"""


def safe_rate(numerator: int, denominator: int) -> float | None:
    """`numerator / denominator`, ou `None` se não houver denominador.

    `None` (não `0.0`) de propósito: "nenhum NBA foi gerado ainda" é um
    estado diferente de "NBA foi gerado, mas ninguém clicou" — misturar os
    dois no mesmo `0.0` esconderia a diferença de quem for ler a métrica.
    """
    if denominator == 0:
        return None
    return numerator / denominator
