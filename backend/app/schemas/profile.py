"""Schemas Pydantic da Tela de Perfil (EPIC 09) e do aviso ao responsável
(EPIC 17).

Compõe os dados cadastrais do usuário com um resumo de gamificação (nível, XP e
contadores). Dados sensíveis: o CPF é retornado **mascarado** (nunca completo).
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.gamification import LevelInfo


class ProfileStats(BaseModel):
    """Resumo de gamificação do candidato exibido no perfil."""

    level: LevelInfo
    missions_completed: int
    achievements_unlocked: int
    rewards_redeemed: int


class ProfileResponse(BaseModel):
    """Payload de `GET /api/v1/profile`."""

    id: uuid.UUID
    name: str
    email: str
    # CPF mascarado (ex.: "123.***.***-09") — nunca o número completo.
    cpf_masked: str
    phone: str
    member_since: datetime
    stats: ProfileStats
    # Entrevista com o responsável (EPIC 17).
    interview_date: date | None
    interview_location: str
    guardian_name: str | None
    guardian_phone: str | None
    guardian_email: str | None
    guardian_notified_at: datetime | None
    # Formação obrigatória do responsável (item 5 do backlog — confirmação
    # de presença pelo próprio responsável, via link mágico).
    guardian_training_date: date | None
    guardian_training_notified_at: datetime | None
    guardian_training_confirmed_at: datetime | None
    guardian_training_attended_at: datetime | None
    # None = sem responsável cadastrado ainda (não há link para gerar).
    guardian_portal_url: str | None


class ProfileUpdateRequest(BaseModel):
    """Campos editáveis do perfil (`PATCH /api/v1/profile`)."""

    name: str = Field(min_length=2, max_length=150)
    # Telefone só com dígitos (DDD + número): 10 ou 11 dígitos.
    phone: str = Field(min_length=10, max_length=11)
    # Contato do responsável — todos opcionais (nem todo candidato preenche de
    # uma vez), mas validados quando informados. `None`/vazio limpa o campo.
    guardian_name: str | None = Field(default=None, max_length=150)
    guardian_phone: str | None = Field(default=None)
    guardian_email: EmailStr | None = Field(default=None)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 2:
            raise ValueError("Nome muito curto.")
        return stripped

    @field_validator("phone")
    @classmethod
    def _digits_only(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) not in (10, 11):
            raise ValueError("Telefone deve ter 10 ou 11 dígitos (DDD + número).")
        return digits

    @field_validator("guardian_name")
    @classmethod
    def _strip_guardian_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("guardian_phone")
    @classmethod
    def _validate_guardian_phone(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) not in (10, 11):
            raise ValueError("Telefone do responsável deve ter 10 ou 11 dígitos.")
        return digits


class GuardianEmailNoticeResult(BaseModel):
    """Payload de `POST /api/v1/profile/guardian/notify-email`."""

    sent: bool
    message: str
    guardian_notified_at: datetime | None


class GuardianTrainingEmailNoticeResult(BaseModel):
    """Payload de `POST /api/v1/profile/guardian/notify-training`."""

    sent: bool
    message: str
    guardian_training_notified_at: datetime | None
