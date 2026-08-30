"""Contrato da Pausa Declarada ("Jornada que Respira" — fase 1).

- `POST /candidate/pause`         → inicia a pausa;
- `POST /candidate/pause/resume`  → retoma e devolve o ponto guardado.

O estado da pausa também aparece em `GET /candidate-state` (campo `pause`),
para o Dashboard não precisar de uma segunda chamada só para saber se deve
renderizar a experiência calma.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.journey_pause_rules import PAUSE_OPTION_DAYS, PauseReasonCode


class PauseStartRequest(BaseModel):
    """Corpo de `POST /candidate/pause`.

    Sem texto livre em nenhum campo — o público inclui menores, e a única
    coisa que o produto precisa saber é "por quanto tempo" (e, opcionalmente,
    uma categoria genérica de motivo).
    """

    days: int = Field(description=f"Período pedido. Só as opções {PAUSE_OPTION_DAYS} são aceitas.")
    reason_code: PauseReasonCode | None = None

    @field_validator("days")
    @classmethod
    def _validate_option(cls, value: int) -> int:
        if value not in PAUSE_OPTION_DAYS:
            options = " ou ".join(str(day) for day in PAUSE_OPTION_DAYS)
            raise ValueError(f"Período inválido. Escolha {options} dias.")
        return value


class PauseState(BaseModel):
    """A pausa em curso, como o candidato a enxerga.

    Nunca inclui `reason_code` de outros candidatos nem qualquer sinal de
    risco — é só "até quando" e "o que você ia fazer".
    """

    model_config = ConfigDict(from_attributes=True)

    ends_at: datetime
    reason_code: PauseReasonCode | None
    #: `NextBestActionKey` guardada no início da pausa — o que torna a volta
    #: de 1 toque. `None` quando não havia recomendação acionável.
    resume_action_key: str | None


class PauseResumeResult(BaseModel):
    """Payload de `POST /candidate/pause/resume`."""

    resumed: bool
    resume_action_key: str | None
