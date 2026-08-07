"""create cohorts, coordinator_cohorts, activity_events; add users.role and cohort_id

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-06 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). Fases 1 e 2 da
EPIC 14 (Predição de evasão). Espelha:
- `app.models.cohort.Cohort` / `CoordinatorCohort` (coorte + escopo do RBAC);
- `app.models.user.User.role` (papel: candidate/coordinator/admin);
- `app.models.candidate_profile.CandidateProfile.cohort_id`;
- `app.models.activity_event.ActivityEvent` (log comportamental append-only).

Backfill: usuários com `is_admin=true` recebem `role='admin'`, mantendo o
painel administrativo existente funcionando sem ruptura.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: str | None = "e5f6a7b8c9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- Fase 1: coortes -------------------------------------------------
    op.create_table(
        "cohorts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(length=10), nullable=False),
        sa.Column("exam_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
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
        sa.UniqueConstraint("year", "term", name="uq_cohort_year_term"),
    )
    op.create_index(op.f("ix_cohorts_is_active"), "cohorts", ["is_active"])

    op.create_table(
        "coordinator_cohorts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "cohort_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cohorts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "cohort_id", name="uq_coordinator_cohort_user_cohort"),
    )
    op.create_index(op.f("ix_coordinator_cohorts_user_id"), "coordinator_cohorts", ["user_id"])
    op.create_index(op.f("ix_coordinator_cohorts_cohort_id"), "coordinator_cohorts", ["cohort_id"])

    # --- Fase 1: papel do usuário ---------------------------------------
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), server_default="candidate", nullable=False),
    )
    op.create_check_constraint(
        "ck_user_role",
        "users",
        "role IN ('candidate', 'coordinator', 'admin')",
    )
    op.create_index(op.f("ix_users_role"), "users", ["role"])
    # Backfill: quem já era admin pelo booleano legado continua admin no RBAC.
    op.execute("UPDATE users SET role = 'admin' WHERE is_admin IS TRUE")

    # --- Fase 1: coorte do candidato ------------------------------------
    op.add_column(
        "candidate_profiles",
        sa.Column(
            "cohort_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cohorts.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(op.f("ix_candidate_profiles_cohort_id"), "candidate_profiles", ["cohort_id"])

    # --- Fase 2: log comportamental --------------------------------------
    op.create_table(
        "activity_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column(
            "props",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "name IN ('login', 'step_viewed', 'step_completed', 'mission_started', "
            "'mission_completed', 'mission_abandoned', 'document_uploaded')",
            name="ck_activity_event_name",
        ),
    )
    # Índice composto: a derivação de features lê sempre "eventos deste
    # candidato, do mais recente para trás" — sem ele, viraria full scan.
    op.create_index(
        "ix_activity_events_candidate_occurred",
        "activity_events",
        ["candidate_profile_id", "occurred_at"],
    )
    op.create_index(
        "ix_activity_events_name_occurred",
        "activity_events",
        ["name", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_activity_events_name_occurred", table_name="activity_events")
    op.drop_index("ix_activity_events_candidate_occurred", table_name="activity_events")
    op.drop_table("activity_events")

    op.drop_index(op.f("ix_candidate_profiles_cohort_id"), table_name="candidate_profiles")
    op.drop_column("candidate_profiles", "cohort_id")

    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_constraint("ck_user_role", "users", type_="check")
    op.drop_column("users", "role")

    op.drop_index(op.f("ix_coordinator_cohorts_cohort_id"), table_name="coordinator_cohorts")
    op.drop_index(op.f("ix_coordinator_cohorts_user_id"), table_name="coordinator_cohorts")
    op.drop_table("coordinator_cohorts")

    op.drop_index(op.f("ix_cohorts_is_active"), table_name="cohorts")
    op.drop_table("cohorts")
