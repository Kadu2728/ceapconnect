"""Model SQLAlchemy de `GuardianCandidateLink` (RBAC do responsável).

É a camada de **autorização** — quem pode logar como responsável e ver quem
— separada de `app.models.guardian.Guardian`, que continua sendo o registro
de contato/jornada por candidato (nome, telefone, formação obrigatória etc.)
e não muda nesta feature.

Por que uma tabela nova em vez de acoplar a autorização em `Guardian`: uma
mesma pessoa pode ser responsável por mais de um candidato (irmãos no
CEAP), mas `Guardian` é uma linha por candidato, sem nenhuma identidade que
amarre duas linhas à mesma pessoa. `GuardianCandidateLink` é essa amarração
— aponta para o `User` (a conta de login), não duplica nome/telefone/e-mail,
que continuam só em `Guardian`.
"""

import uuid
from typing import Final, Literal

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin

ConsentStatus = Literal["not_required", "pending", "granted", "revoked"]

CONSENT_NOT_REQUIRED: Final = "not_required"
CONSENT_PENDING: Final = "pending"
CONSENT_GRANTED: Final = "granted"
CONSENT_REVOKED: Final = "revoked"

_VALID_CONSENT_STATUSES: Final = (
    CONSENT_NOT_REQUIRED,
    CONSENT_PENDING,
    CONSENT_GRANTED,
    CONSENT_REVOKED,
)

# Estados que autorizam acesso de fato — usado por `GuardianScope`
# (`app.core.rbac`) para filtrar a query, nunca em memória.
AUTHORIZED_CONSENT_STATUSES: Final = (CONSENT_NOT_REQUIRED, CONSENT_GRANTED)


class GuardianCandidateLink(Base, TimestampMixin):
    """Vínculo de autorização entre a conta de login do responsável e um candidato."""

    __tablename__ = "guardian_candidate_links"
    __table_args__ = (
        CheckConstraint(
            f"consent_status IN {_VALID_CONSENT_STATUSES}", name="ck_guardian_link_consent_status"
        ),
        UniqueConstraint(
            "guardian_user_id", "candidate_profile_id", name="uq_guardian_link_user_candidate"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    guardian_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # `not_required` existe para candidato menor de idade (regra do produto:
    # menor não precisa consentir o próprio responsável acompanhando) — mas
    # o cadastro hoje não coleta data de nascimento em lugar nenhum do
    # sistema (`User`/`CandidateProfile`), então não há como o backend
    # decidir maioridade sozinho ainda. Até essa coleta existir, todo vínculo
    # novo nasce `pending` — o candidato sempre precisa consentir
    # explicitamente, é o padrão mais conservador dado o dado que falta,
    # nunca `not_required` por suposição.
    consent_status: Mapped[ConsentStatus] = mapped_column(
        String(20), default=CONSENT_PENDING, server_default=CONSENT_PENDING, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<GuardianCandidateLink guardian_user_id={self.guardian_user_id} "
            f"candidate_profile_id={self.candidate_profile_id} status={self.consent_status}>"
        )
