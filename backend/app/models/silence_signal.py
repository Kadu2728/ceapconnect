"""Model SQLAlchemy de `SilenceSignal` (Radar de Silêncio — "Jornada que Respira").

Registra o **momento em que um candidato cruzou** de ativo para silencioso.
Isso é o que o Radar acrescenta ao que já existia: o motor de risco já mede,
pontua (`_WEIGHT_INACTIVITY`, o maior peso comportamental do modelo) e exibe
silêncio ao coordenador — mas como um *estado* que ele precisa ir procurar na
fila. O sinal aqui é o *evento da travessia*, que permite responder "quem
entrou em silêncio esta semana?" em vez de só "quem está em silêncio agora?".

**Por que não é um `ActivityEvent`** (a escolha mais óbvia, e que quebraria a
feature): `risk_feature_service` deriva `days_since_last_activity` de
`MAX(activity_events.occurred_at)` do candidato. Gravar o silêncio no log
comportamental faria o candidato parecer **ativo** no instante exato em que
foi detectado como silencioso — o Radar apagaria o próprio sinal que acabou
de emitir. O log de eventos é do que o candidato *fez*; isto é uma inferência
do sistema *sobre* ele, e as duas coisas não podem morar na mesma tabela.

Nunca é exibido ao candidato: silêncio é sinal operacional para o
coordenador, no mesmo espírito do score de risco (que o candidato também
jamais vê).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class SilenceSignal(Base, TimestampMixin):
    """Uma travessia para o silêncio, e (quando acontece) a volta."""

    __tablename__ = "silence_signals"
    __table_args__ = (
        # Um único sinal aberto por candidato: sem isso, cada passada do job
        # de risco (de hora em hora) criaria uma linha nova para a mesma
        # pessoa silenciosa, e "quem entrou em silêncio esta semana" viraria
        # uma contagem de execuções do job, não de pessoas.
        Index(
            "uq_silence_signal_one_open",
            "candidate_profile_id",
            unique=True,
            postgresql_where=text("returned_at IS NULL"),
        ),
        Index("ix_silence_signals_detected_at", "detected_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    #: Dias de inatividade no momento da detecção. Guardado porque o job roda
    #: de hora em hora e pode pegar a travessia com alguma folga — sem isso,
    #: não dá para distinguir "cruzou o limiar agora" de "já estava em
    #: silêncio quando o Radar entrou no ar".
    days_silent: Mapped[float] = mapped_column(Float, nullable=False)
    #: Etapa em que o candidato emudeceu — responde "onde as pessoas somem?",
    #: que é a pergunta do funil de conversão inscrição→prova. Sem FK, mesmo
    #: tratamento de `journey_pauses.paused_at_step_key`: valor histórico não
    #: deve travar a evolução do catálogo de etapas.
    step_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    #: `None` = ainda em silêncio. Preenchido quando o candidato volta a dar
    #: sinal de vida — é esse par (detected_at, returned_at) que sustenta a
    #: taxa de retorno após silêncio, espelhando a de retorno após pausa.
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<SilenceSignal candidate_profile_id={self.candidate_profile_id} "
            f"detected_at={self.detected_at} returned_at={self.returned_at}>"
        )
