"""Regras de disparo dos lembretes automáticos.

Camada de domínio **pura** (sem I/O): recebe os dados já resolvidos do
candidato e devolve só `True`/`False` para cada janela de lembrete. Nenhuma
regra aqui decide "já foi enviado" — isso é `ReminderLog`
(`reminder_service.py` cruza as duas coisas).

Janelas em "até N dias" (não "exatamente N dias") de propósito: o job roda a
cada `REMINDER_CHECK_INTERVAL_MINUTES`, não precisamente à meia-noite, e uma
janela exata perderia o disparo se o processo estivesse fora do ar bem no
momento exato. Cada janela só dispara uma vez por candidato de qualquer
forma (`ReminderLog`), então "até N dias" nunca gera duplicata — só garante
que o lembrete sai mesmo com alguma folga de tempo.
"""

from typing import Final

# Dias de tolerância desde o cadastro antes de cobrar documentação
# pendente — mesma ordem de grandeza do limiar de "travado numa etapa
# bloqueante" usado pelo motor de risco (`risk_feature_service.
# STUCK_THRESHOLD_DAYS`), mas definido à parte: um é sinal de risco para o
# coordenador, o outro é um lembrete direto ao candidato — propósitos
# diferentes, não deveriam compartilhar a mesma constante por coincidência
# de valor.
DOCUMENTATION_REMINDER_AFTER_DAYS: Final = 5.0

_EXAM_7_DAYS_WINDOW: Final = 7
_EXAM_1_DAY_WINDOW: Final = 1
_INTERVIEW_7_DAYS_WINDOW: Final = 7
_INTERVIEW_1_DAY_WINDOW: Final = 1


def _within_window(days_until: int | None, window: int) -> bool:
    """`True` se o evento ainda não passou e está a `window` dias ou menos."""
    return days_until is not None and 0 <= days_until <= window


def should_remind_exam_7_days(days_to_exam: int | None) -> bool:
    return _within_window(days_to_exam, _EXAM_7_DAYS_WINDOW)


def should_remind_exam_1_day(days_to_exam: int | None) -> bool:
    return _within_window(days_to_exam, _EXAM_1_DAY_WINDOW)


def should_remind_interview_7_days(days_to_interview: int | None) -> bool:
    return _within_window(days_to_interview, _INTERVIEW_7_DAYS_WINDOW)


def should_remind_interview_1_day(days_to_interview: int | None) -> bool:
    return _within_window(days_to_interview, _INTERVIEW_1_DAY_WINDOW)


def should_remind_documentation_incomplete(
    *, days_since_registration: float, pending_documents: int
) -> bool:
    return pending_documents > 0 and days_since_registration >= DOCUMENTATION_REMINDER_AFTER_DAYS
