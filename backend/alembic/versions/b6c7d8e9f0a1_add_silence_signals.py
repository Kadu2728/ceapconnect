"""add silence_signals (Radar de Silêncio — Jornada que Respira, metade B)

Revision ID: b6c7d8e9f0a1
Revises: a5b6c7d8e9f0
Create Date: 2026-08-30 00:00:00.000000

Registra a travessia de ativo para silencioso — o que o Radar acrescenta ao
motor de risco, que já media e exibia silêncio como *estado*, mas não como
*evento*.

Tabela própria (não `activity_events`) porque o log comportamental alimenta
`MAX(occurred_at)` = "última atividade": gravar o silêncio lá faria o
candidato parecer ativo no instante em que foi detectado silencioso.

Aditivo: nenhuma tabela ou rota existente muda de comportamento.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b6c7d8e9f0a1"
down_revision: str | None = "a5b6c7d8e9f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "silence_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("days_silent", sa.Float(), nullable=False),
        sa.Column("step_key", sa.String(length=50), nullable=True),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
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
    )

    # Um sinal aberto por candidato — sem isso o job (de hora em hora) criaria
    # uma linha nova por passada para a mesma pessoa.
    op.create_index(
        "uq_silence_signal_one_open",
        "silence_signals",
        ["candidate_profile_id"],
        unique=True,
        postgresql_where=sa.text("returned_at IS NULL"),
    )
    op.create_index("ix_silence_signals_detected_at", "silence_signals", ["detected_at"])


def downgrade() -> None:
    op.drop_index("ix_silence_signals_detected_at", table_name="silence_signals")
    op.drop_index("uq_silence_signal_one_open", table_name="silence_signals")
    op.drop_table("silence_signals")
