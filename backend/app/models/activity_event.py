"""Model SQLAlchemy da entidade `ActivityEvent` (EPIC 14 — Predição de evasão).

Log **append-only** de eventos comportamentais do candidato. É a matéria-prima
da derivação de features do modelo de risco: nada é calculado aqui — só se
registra o que aconteceu, com um `props` livre (JSONB) para o contexto.

**Nome:** a spec chamava esta entidade de `events`, mas esse nome (tabela e
classe `Event`) já pertence ao catálogo de eventos da comunidade — palestras,
simulados (EPIC 07). Para não colidir, o log comportamental é
`ActivityEvent`/`activity_events`; a estrutura e os índices são os aprovados.

Não usa `TimestampMixin` nem soft delete de propósito: `occurred_at` já cumpre
o papel de "quando isto aconteceu" e um log de eventos nunca é atualizado nem
apagado logicamente.

Índice `(candidate_profile_id, occurred_at)`: a derivação de features sempre lê
"os eventos deste candidato, do mais recente para trás" — sem esse índice
composto, o cálculo viraria full scan com milhares de candidatos.
"""

import uuid
from datetime import datetime
from typing import Any, Final, Literal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

ActivityEventName = Literal[
    "login",
    "step_viewed",
    "step_completed",
    "step_abandoned",
    "step_resumed",
    "mission_started",
    "mission_completed",
    "mission_abandoned",
    "document_uploaded",
    "nba_generated",
    "nba_clicked",
    "nba_completed",
    "recovery_entered",
    "recovery_completed",
    "recovery_exited",
    "pause_started",
    "pause_resumed",
    "pause_expired",
]

EVENT_LOGIN: Final = "login"
EVENT_STEP_VIEWED: Final = "step_viewed"
EVENT_STEP_COMPLETED: Final = "step_completed"
# Candidate Journey OS — fundação F1 (taxonomia de eventos do Candidate
# State / Next Best Action / Zero-Click Recovery / Modo Resgate). Nenhum
# nome antigo foi renomeado: `step_viewed`/`step_completed` já cobrem
# "started/completed" da spec original do brief, então só o que faltava
# (abandono, retomada, e os três novos consumidores) foi acrescentado —
# estender uma migration de CHECK constraint é seguro, renomear valores
# históricos já gravados não seria.
EVENT_STEP_ABANDONED: Final = "step_abandoned"
EVENT_STEP_RESUMED: Final = "step_resumed"
EVENT_MISSION_STARTED: Final = "mission_started"
EVENT_MISSION_COMPLETED: Final = "mission_completed"
EVENT_MISSION_ABANDONED: Final = "mission_abandoned"
EVENT_DOCUMENT_UPLOADED: Final = "document_uploaded"
# Next Best Action Engine (N2): ciclo gerado → clicado → concluído, base do
# Learning Loop (F2) para medir CTR e conclusão por recomendação.
EVENT_NBA_GENERATED: Final = "nba_generated"
EVENT_NBA_CLICKED: Final = "nba_clicked"
EVENT_NBA_COMPLETED: Final = "nba_completed"
# Modo Resgate (N4): ativação, conclusão da ação única apresentada, e saída
# sem concluir (candidato voltou à jornada normal por conta própria ou por
# o estado ter melhorado) — os três suficientes para medir conversão do
# modo sem duplicar o que `nba_*` já mede sobre a ação em si.
EVENT_RECOVERY_ENTERED: Final = "recovery_entered"
EVENT_RECOVERY_COMPLETED: Final = "recovery_completed"
EVENT_RECOVERY_EXITED: Final = "recovery_exited"
# Pausa Declarada ("Jornada que Respira" — fase 1): três momentos reais e
# distintos. Não existe um `pause_requested` separado de `pause_started`
# porque não há etapa de aprovação entre os dois — seriam duas linhas para o
# mesmo instante. `pause_resumed` (voltou por vontade própria) e
# `pause_expired` (deixou o prazo passar) são o par que sustenta a métrica
# principal da feature: taxa de retorno após pausa.
EVENT_PAUSE_STARTED: Final = "pause_started"
EVENT_PAUSE_RESUMED: Final = "pause_resumed"
EVENT_PAUSE_EXPIRED: Final = "pause_expired"

# Vocabulário fechado de eventos (CHECK constraint). `mission_completed` não
# estava na lista original da spec, mas é emitido por um fluxo que já existe
# (conclusão de missão) e alimenta diretamente a feature "razão de etapas
# concluídas" — sem ele, o progresso positivo do candidato ficaria invisível
# para o modelo.
_VALID_EVENT_NAMES: Final = (
    EVENT_LOGIN,
    EVENT_STEP_VIEWED,
    EVENT_STEP_COMPLETED,
    EVENT_STEP_ABANDONED,
    EVENT_STEP_RESUMED,
    EVENT_MISSION_STARTED,
    EVENT_MISSION_COMPLETED,
    EVENT_MISSION_ABANDONED,
    EVENT_DOCUMENT_UPLOADED,
    EVENT_NBA_GENERATED,
    EVENT_NBA_CLICKED,
    EVENT_NBA_COMPLETED,
    EVENT_RECOVERY_ENTERED,
    EVENT_RECOVERY_COMPLETED,
    EVENT_RECOVERY_EXITED,
    EVENT_PAUSE_STARTED,
    EVENT_PAUSE_RESUMED,
    EVENT_PAUSE_EXPIRED,
)


class ActivityEvent(Base):
    """Evento comportamental de um candidato (append-only)."""

    __tablename__ = "activity_events"
    __table_args__ = (
        CheckConstraint(f"name IN {_VALID_EVENT_NAMES}", name="ck_activity_event_name"),
        Index(
            "ix_activity_events_candidate_occurred",
            "candidate_profile_id",
            "occurred_at",
        ),
        Index("ix_activity_events_name_occurred", "name", "occurred_at"),
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
    name: Mapped[ActivityEventName] = mapped_column(String(50), nullable=False)
    # Contexto livre do evento (ex.: {"step_key": "documentacao"}). JSONB para
    # permitir consulta/filtragem no banco se necessário no futuro.
    props: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}", nullable=False
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ActivityEvent name={self.name} candidate_profile_id={self.candidate_profile_id}>"
