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

import secrets
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


def _generate_confirmation_token() -> str:
    """Token de posse do link mágico do responsável — 32 bytes, URL-safe.

    Não é um segredo derivado de nada (ex.: hash do id) de propósito: um
    token opaco e imprevisível é o que torna seguro expor a confirmação sem
    exigir conta/login do responsável (mesmo racional de link de reset de
    senha — posse do link autoriza a ação).
    """
    return secrets.token_urlsafe(32)


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
    # Link mágico do responsável (item 5 do backlog — "confirmação de
    # presença pelo próprio responsável"): identifica o responsável sem
    # exigir conta/login, em `GET/POST /guardian-portal/{token}`. Único por
    # responsável, gerado na criação — nunca reaproveitado nem regenerado
    # automaticamente (um link já enviado por e-mail/WhatsApp precisa
    # continuar válido).
    confirmation_token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        default=_generate_confirmation_token,
        nullable=False,
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
    # Aviso da formação obrigatória (distinto do aviso da entrevista acima —
    # são dois eventos diferentes, com datas diferentes).
    training_notice_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # RBAC do responsável — fase B (ativação de conta): marca que ESTE
    # registro de contato já foi usado para criar uma conta de login
    # (`User.role == "guardian"`). Torna a ativação idempotente (mesmo link
    # clicado duas vezes não cria uma segunda conta) e permite ao portal
    # público mostrar "faça login" em vez do formulário de cadastro depois
    # da primeira ativação. `ondelete="SET NULL"`: se a conta de login for
    # removida, o contato continua válido — só deixa de estar "ativado".
    activated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Guardian id={self.id} candidate_profile_id={self.candidate_profile_id}>"
