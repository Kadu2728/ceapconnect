"""create cohort_xp_standing materialized view

Revision ID: a3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-08-19 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). Fase 4
(otimizações medidas): pré-calcula o percentil de XP por coorte — hoje
recalculado via agregação ao vivo em toda carga do Dashboard
(`CohortStatsRepository.xp_standing`) — numa materialized view, atualizada
periodicamente pelo scheduler (`app.core.scheduler`), em vez de a cada
request. Espelha `app.models.cohort_xp_standing.CohortXpStanding`.

A janela `COUNT(*) OVER (... ORDER BY xp_total RANGE BETWEEN UNBOUNDED
PRECEDING AND CURRENT ROW)` usa RANGE (não ROWS) de propósito: com RANGE,
candidatos empatados em XP contam uns aos outros como "menor ou igual" — é a
mesma semântica de "quantos têm XP <= o meu" que a query antiga fazia com
`COUNT(*) FILTER (WHERE xp_total <= :valor)`.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a3b4c5d6e7f8"
down_revision: str | None = "f2a3b4c5d6e7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        CREATE MATERIALIZED VIEW cohort_xp_standing AS
        SELECT
            cp.id AS candidate_profile_id,
            cp.cohort_id AS cohort_id,
            COUNT(*) OVER (PARTITION BY cp.cohort_id) AS total,
            COUNT(*) OVER (
                PARTITION BY cp.cohort_id
                ORDER BY cp.xp_total
                RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS at_or_below
        FROM candidate_profiles cp
        JOIN users u ON u.id = cp.user_id
        WHERE cp.deleted_at IS NULL
          AND u.deleted_at IS NULL
          AND u.role = 'candidate'
          AND cp.cohort_id IS NOT NULL
    """)
    op.execute(
        "CREATE INDEX ix_cohort_xp_standing_candidate ON cohort_xp_standing (candidate_profile_id)"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS cohort_xp_standing")
