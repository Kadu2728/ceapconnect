"""create simulado tables

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-08-09 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). EPIC 16
(Simulados de prova). Espelha `app.models.simulado.{SimuladoQuestion,
SimuladoAttempt, SimuladoAnswer}`.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: str | None = "b8c9d0e1f2a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "simulado_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("subject", sa.String(length=20), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("correct_option_key", sa.String(length=5), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "subject IN ('portugues', 'matematica')", name="ck_simulado_question_subject"
        ),
    )
    op.create_index(op.f("ix_simulado_questions_subject"), "simulado_questions", ["subject"])

    op.create_table(
        "simulado_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_simulado_attempts_candidate_profile_id"),
        "simulado_attempts",
        ["candidate_profile_id"],
    )

    op.create_table(
        "simulado_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "attempt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("simulado_attempts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("simulado_questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("selected_option_key", sa.String(length=5), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column(
            "answered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "attempt_id", "question_id", name="uq_simulado_answer_attempt_question"
        ),
    )
    op.create_index(op.f("ix_simulado_answers_attempt_id"), "simulado_answers", ["attempt_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_simulado_answers_attempt_id"), table_name="simulado_answers")
    op.drop_table("simulado_answers")

    op.drop_index(op.f("ix_simulado_attempts_candidate_profile_id"), table_name="simulado_attempts")
    op.drop_table("simulado_attempts")

    op.drop_index(op.f("ix_simulado_questions_subject"), table_name="simulado_questions")
    op.drop_table("simulado_questions")
