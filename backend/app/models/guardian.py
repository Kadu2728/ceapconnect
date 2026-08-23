"""Model SQLAlchemy da entidade `Guardian` (responsável — Frente KPI conversão + responsável).

Substitui os campos planos `guardian_name`/`guardian_phone`/`guardian_email`/
`guardian_notified_at` que viviam direto em `CandidateProfile` (EPIC 17): a
mentoria do CEAP identificou o responsável como fator de evasão de primeira
ordem — um candidato pode ter mais de um responsável, e o produto agora
precisa rastrear a jornada dele (formação obrigatória), não só o contato.

Um candidato pode ter mais de um `Guardian` (por isso não há UNIQUE em
`candidate_profile_id`); `is_primary` marca qual deles recebe o aviso da
entrevista por padrão e é o único editável pela tela de Perfil atual — os
demais entram por um fluxo próprio (fase futura).

**Nunca contamina o sinal do candidato**: os marcos aqui (`training_*_at`)
são sempre do responsável. Nenhum deles altera `CandidateProfile.xp_total` —
ver `app.services.achievement_service` para o desbloqueio simbólico
(sem XP) do marco "responsável concluiu a formação".
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class Guardian(Base, TimestampMixin):
    """Responsável legal vinculado a um candidato."""

    __tablename__ = "guardians"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(11), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Ex.: "mãe", "pai", "avó", "responsável legal" — texto livre e curto de
    # propósito (famílias reais não cabem num enum fechado), nunca exibido
    # como campo de busca/análise, só como rótulo de contexto na UI.
    relationship_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    # --- Jornada do responsável (formação obrigatória) ----------------------
    # Confirmação de presença (o responsável ou o candidato avisa que vai) —
    # sinal leve. `training_attended_at` é o que de fato zera o risco.
    training_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    training_attended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Substitui `CandidateProfile.guardian_notified_at` (EPIC 17).
    interview_notice_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Guardian id={self.id} candidate_profile_id={self.candidate_profile_id}>"
