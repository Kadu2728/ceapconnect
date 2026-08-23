"""create guardians table, migrate guardian fields, add cohort training date

Revision ID: c5d6e7f8a9b0
Revises: a3b4c5d6e7f8
Create Date: 2026-08-20 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). Primeira peça da
iniciativa KPI de conversão + responsável: a mentoria do CEAP identificou o
responsável como fator de evasão de primeira ordem (se não participa da
formação obrigatória, o candidato perde a vaga) — o produto até aqui só
modelava o candidato.

- `guardians`: substitui `candidate_profiles.guardian_name/phone/email/
  notified_at` (EPIC 17, 4 colunas planas, um único responsável). Um
  candidato pode ter mais de um responsável — não cabia mais em colunas
  soltas. Backfill: uma linha (`is_primary=true`) por perfil que já tinha
  algum dado de contato preenchido; `guardian_notified_at` vira
  `interview_notice_sent_at`.
- `cohorts.guardian_training_date`: data única da formação obrigatória de
  pais, compartilhada por toda a coorte (confirmado com o time do CEAP —
  não há múltiplas sessões à escolha nesta fase).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "c5d6e7f8a9b0"
down_revision: str | None = "a3b4c5d6e7f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "guardians",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=150), nullable=True),
        sa.Column("phone", sa.String(length=11), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("relationship_label", sa.String(length=50), nullable=True),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("training_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("training_attended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("interview_notice_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        op.f("ix_guardians_candidate_profile_id"), "guardians", ["candidate_profile_id"]
    )

    # Backfill: 1 guardian por perfil que já tinha algum contato preenchido.
    # gen_random_uuid() é built-in do Postgres (core, desde a v13) — sem
    # depender da extensão pgcrypto.
    op.execute("""
        INSERT INTO guardians (
            id, candidate_profile_id, name, phone, email, is_primary,
            interview_notice_sent_at, created_at, updated_at
        )
        SELECT
            gen_random_uuid(), id, guardian_name, guardian_phone, guardian_email, true,
            guardian_notified_at, now(), now()
        FROM candidate_profiles
        WHERE guardian_name IS NOT NULL
           OR guardian_phone IS NOT NULL
           OR guardian_email IS NOT NULL
           OR guardian_notified_at IS NOT NULL
    """)

    op.drop_column("candidate_profiles", "guardian_name")
    op.drop_column("candidate_profiles", "guardian_phone")
    op.drop_column("candidate_profiles", "guardian_email")
    op.drop_column("candidate_profiles", "guardian_notified_at")

    op.add_column("cohorts", sa.Column("guardian_training_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("cohorts", "guardian_training_date")

    op.add_column(
        "candidate_profiles", sa.Column("guardian_name", sa.String(length=150), nullable=True)
    )
    op.add_column(
        "candidate_profiles", sa.Column("guardian_phone", sa.String(length=11), nullable=True)
    )
    op.add_column(
        "candidate_profiles", sa.Column("guardian_email", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "candidate_profiles",
        sa.Column("guardian_notified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute("""
        UPDATE candidate_profiles cp
        SET
            guardian_name = g.name,
            guardian_phone = g.phone,
            guardian_email = g.email,
            guardian_notified_at = g.interview_notice_sent_at
        FROM guardians g
        WHERE g.candidate_profile_id = cp.id AND g.is_primary IS TRUE
    """)

    op.drop_index(op.f("ix_guardians_candidate_profile_id"), table_name="guardians")
    op.drop_table("guardians")
