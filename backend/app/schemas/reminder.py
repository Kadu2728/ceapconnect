"""Contrato de `POST /internal/reminders/check` (lembretes automáticos)."""

from pydantic import BaseModel


class ReminderCheckSummary(BaseModel):
    """Payload de resposta do disparo (agendado ou manual) de lembretes."""

    candidates_checked: int
    reminders_sent: int
    duration_seconds: float
