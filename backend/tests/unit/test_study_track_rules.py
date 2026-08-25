"""Testes de `app.core.study_track_rules` (trilha de estudo). Sem I/O, sem banco."""

from app.core.study_track_rules import resolve_weakest_subject


def test_aponta_a_materia_com_menor_taxa_de_acerto() -> None:
    breakdown = [("portugues", 9, 10), ("matematica", 4, 10)]
    assert resolve_weakest_subject(breakdown) == "matematica"


def test_empate_exato_nao_aponta_nenhuma() -> None:
    breakdown = [("portugues", 5, 10), ("matematica", 5, 10)]
    assert resolve_weakest_subject(breakdown) is None


def test_menos_de_duas_materias_com_dado_nao_aponta_nenhuma() -> None:
    assert resolve_weakest_subject([("portugues", 8, 10)]) is None
    assert resolve_weakest_subject([]) is None


def test_materia_sem_nenhuma_questao_respondida_e_ignorada() -> None:
    breakdown = [("portugues", 8, 10), ("matematica", 0, 0)]
    assert resolve_weakest_subject(breakdown) is None


def test_taxa_de_acerto_importa_mais_que_contagem_absoluta() -> None:
    # Português: 90% (9/10). Matemática: 80% (4/5) — menos erros em número
    # absoluto, mas taxa pior.
    breakdown = [("portugues", 9, 10), ("matematica", 4, 5)]
    assert resolve_weakest_subject(breakdown) == "matematica"
