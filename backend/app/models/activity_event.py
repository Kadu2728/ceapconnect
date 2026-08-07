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
    "mission_started",
    "mission_completed",
    "mission_abandoned",
    "document_uploaded",
]

EVENT_LOGIN: Final = "login"
EVENT_STEP_VIEWED: Final = "step_viewed"
EVENT_STEP_COMPLETED: Final = "step_completed"
EVENT_MISSION_STARTED: Final = "mission_started"
EVENT_MISSION_COMPLETED: Final = "mission_completed"
EVENT_MISSION_ABANDONED: Final = "mission_abandoned"
EVENT_DOCUMENT_UPLOADED: Final = "document_uploaded"

# Vocabulário fechado de eventos (CHECK constraint). `mission_completed` não
# estava na lista original da spec, mas é emitido por um fluxo que já existe
# (conclusão de missão) e alimenta diretamente a feature "razão de etapas
# concluídas" — sem ele, o progresso positivo do candidato ficaria invisível
# para o modelo.
_VALID_EVENT_NAMES: Final = (
    EVENT_LOGIN,
    EVENT_STEP_VIEWED,
    EVENT_STEP_COMPLETED,
    EVENT_MISSION_STARTED,
    EVENT_MISSION_COMPLETED,
    EVENT_MISSION_ABANDONED,
    EVENT_DOCUMENT_UPLOADED,
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
