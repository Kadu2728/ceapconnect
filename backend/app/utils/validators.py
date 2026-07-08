"""Validadores reutilizáveis de dados de entrada.

Mantidos fora dos schemas Pydantic para permitir reutilização (ex.: em
services, scripts de seed, testes) e para isolar a regra de validação de
onde ela é aplicada.
"""

import re

_ONLY_DIGITS_RE = re.compile(r"\D")


def extract_digits(value: str) -> str:
    """Remove qualquer caractere não numérico de `value`."""
    return _ONLY_DIGITS_RE.sub("", value)


def is_valid_cpf(cpf: str) -> bool:
    """Valida um CPF utilizando o algoritmo oficial de dígitos verificadores.

    Espera `cpf` já normalizado (somente os 11 dígitos, sem máscara).
    Rejeita sequências de dígitos repetidos (ex.: "000.000.000-00",
    "111.111.111-11"), que passam numericamente no cálculo mas nunca são
    CPFs válidos na prática.
    """
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    if len(set(cpf)) == 1:
        return False

    digits = [int(char) for char in cpf]
    first_check_digit = _calculate_cpf_check_digit(digits[:9])
    second_check_digit = _calculate_cpf_check_digit(digits[:9] + [first_check_digit])

    return digits[9] == first_check_digit and digits[10] == second_check_digit


def _calculate_cpf_check_digit(digits: list[int]) -> int:
    """Calcula um dígito verificador do CPF a partir dos dígitos anteriores."""
    weight = len(digits) + 1
    total = sum(digit * (weight - index) for index, digit in enumerate(digits))
    remainder = (total * 10) % 11
    return 0 if remainder == 10 else remainder


def is_valid_phone(phone: str) -> bool:
    """Valida um telefone brasileiro já normalizado (somente dígitos).

    Aceita 10 dígitos (fixo, ex.: DDD + 8 dígitos) ou 11 dígitos
    (celular, ex.: DDD + 9 dígitos, com o nono dígito).
    """
    return phone.isdigit() and len(phone) in (10, 11)
