"""add guardian role + guardian_candidate_links (RBAC do responsável)

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-08-25 00:00:00.000000

Fase A do RBAC do responsável: só papel + autorização relacional, nenhuma
mudança de comportamento em rotas existentes (aditivo).

- `users.role` ganha `'guardian'` (extensão do CHECK constraint existente).
- `guardian_candidate_links`: autorização (quem pode logar como responsável
  e ver quem) — separada de `guardians`, que continua sendo o registro de
  contato/jornada por candidato e não é tocada aqui.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e3f4a5b6c7d8"
down_revision: str | None = "d2e3f4a5b6c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_OLD_ROLES = ("candidate", "coordinator", "admin")
_NEW_ROLES = (*_OLD_ROLES, "guardian")

_CONSENT_STATUSES = ("not_required", "pending", "granted", "revoked")


def upgrade() -> None:
    op.drop_constraint("ck_user_role", "users", type_="check")
    op.create_check_constraint("ck_user_role", "users", "role IN " + str(_NEW_ROLES))

    op.create_table(
        "guardian_candidate_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "guardian_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "consent_status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "consent_status IN " + str(_CONSENT_STATUSES),
            name="ck_guardian_link_consent_status",
        ),
        sa.UniqueConstraint(
            "guardian_user_id", "candidate_profile_id", name="uq_guardian_link_user_candidate"
        ),
    )
    op.create_index(
        "ix_guardian_candidate_links_guardian_user_id",
        "guardian_candidate_links",
        ["guardian_user_id"],
    )
    op.create_index(
        "ix_guardian_candidate_links_candidate_profile_id",
        "guardian_candidate_links",
        ["candidate_profile_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_guardian_candidate_links_candidate_profile_id",
        table_name="guardian_candidate_links",
    )
    op.drop_index(
        "ix_guardian_candidate_links_guardian_user_id", table_name="guardian_candidate_links"
    )
    op.drop_table("guardian_candidate_links")

    op.drop_constraint("ck_user_role", "users", type_="check")
    op.create_check_constraint("ck_user_role", "users", "role IN " + str(_OLD_ROLES))
