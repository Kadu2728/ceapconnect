"""Model SQLAlchemy de `JourneyPause` (Pausa Declarada — "Jornada que Respira").

Registra que o candidato **avisou** que a vida apertou — o oposto de sumir.
É o que transforma abandono silencioso num sinal explícito e datado.

**Por que uma tabela e não colunas em `CandidateProfile`**: a métrica
principal da feature é "de quem pausou, quantos retomaram" — isso exige
histórico. Colunas sobrescreveriam a pausa anterior e a métrica morreria na
segunda pausa do mesmo candidato.

**Nunca é um `CandidateStatus`**: `status` (`active`/`approved`/`evaded`/
`withdrawn`) governa quem entra no recálculo de risco e nos lembretes
(`list_active_candidates`). Um status `paused` congelaria o score do
candidato e contaminaria os rótulos do backtest. Pausa é ortogonal a status —
quem pausou continua ativo no processo seletivo, só pediu um respiro.
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.journey_pause_rules import VALID_REASON_CODES, PauseReasonCode
from app.models.mixins import TimestampMixin

PauseStatus = Literal["active", "resumed", "expired"]

PAUSE_ACTIVE: Final = "active"
#: O candidato voltou por vontade própria (clicou para retomar).
PAUSE_RESUMED: Final = "resumed"
#: A pausa chegou ao fim sem retorno explícito.
PAUSE_EXPIRED: Final = "expired"

# Distinguir as duas formas de terminar é o próprio sinal de produto: um
# único valor "ended" apagaria justamente o que a feature quer medir.
_VALID_STATUSES: Final = (PAUSE_ACTIVE, PAUSE_RESUMED, PAUSE_EXPIRED)


class JourneyPause(Base, TimestampMixin):
    """Uma pausa declarada pelo candidato, com período e desfecho."""

    __tablename__ = "journey_pauses"
    __table_args__ = (
        CheckConstraint(f"status IN {_VALID_STATUSES}", name="ck_journey_pause_status"),
        CheckConstraint(
            f"reason_code IS NULL OR reason_code IN {VALID_REASON_CODES}",
            name="ck_journey_pause_reason",
        ),
        CheckConstraint("ends_at > started_at", name="ck_journey_pause_window"),
        # `ended_at` nulo se e somente se a pausa está em curso — impede o
        # estado impossível de "pausa terminada sem data de término".
        CheckConstraint(
            "(status = 'active') = (ended_at IS NULL)", name="ck_journey_pause_ended_at"
        ),
        # Só UMA pausa ativa por candidato. Invariante garantida pelo banco,
        # não por um `if` no service: sem isso, um duplo clique ou um retry de
        # rede cria duas pausas ativas e o estado do candidato fica ambíguo.
        Index(
            "uq_journey_pause_one_active",
            "candidate_profile_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
        # Histórico do candidato (base da taxa de retorno após pausa).
        Index("ix_journey_pauses_candidate", "candidate_profile_id", "started_at"),
        # Varredura das pausas vencidas pelo job de expiração.
        Index("ix_journey_pauses_due", "ends_at", postgresql_where=text("status = 'active'")),
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

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    #: Já limitado por `journey_pause_rules.resolve_pause_end` (proximidade da prova).
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    #: O que o candidato *pediu*, antes do limite da prova ser aplicado. A
    #: distância entre este valor e `ends_at` revela se a pausa está sendo
    #: oferecida tarde demais na jornada — diagnóstico de produto, não
    #: redundância.
    requested_days: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    #: Opcional e por opções fechadas. **Uso agregado apenas** — nunca exibido
    #: por candidato no Console de Intervenção: mostrar "pausou por trabalho"
    #: ao lado do nome de um menor convida julgamento sobre a vida dele. O
    #: valor está em responder "62% das pausas citam trabalho" (sinal de que o
    #: processo colide com turnos de trabalho), não em rotular alguém.
    reason_code: Mapped[PauseReasonCode | None] = mapped_column(String(20), nullable=True)

    #: Snapshot analítico: em que etapa as pessoas pausam (gargalo do funil).
    #: **Não é alvo de retomada** — `journey_service` continua a única
    #: autoridade sobre onde o candidato está (valor derivado e monotônico).
    #: Sem FK para `journey_steps`, mesmo tratamento de `activity_events.props`:
    #: um valor histórico não deve travar a evolução do catálogo.
    paused_at_step_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    #: A recomendação (Next Best Action) vigente quando a pausa começou — a
    #: única coisa genuinamente efêmera aqui (a etapa não se perde, a
    #: recomendação sim). É o que torna a volta de 1 toque.
    resume_action_key: Mapped[str | None] = mapped_column(String(30), nullable=True)

    status: Mapped[PauseStatus] = mapped_column(
        String(20), default=PAUSE_ACTIVE, server_default=PAUSE_ACTIVE, nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<JourneyPause candidate_profile_id={self.candidate_profile_id} "
            f"status={self.status} ends_at={self.ends_at}>"
        )
