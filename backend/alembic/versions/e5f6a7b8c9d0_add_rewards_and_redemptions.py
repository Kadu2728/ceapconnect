"""create rewards and reward_redemptions

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-22 00:00:00.000000

Migration escrita manualmente (mesmo padrão das anteriores). Espelha:
- `app.models.reward.Reward` (catálogo de recompensas + condição de desbloqueio);
- `app.models.reward_redemption.RewardRedemption` (resgate ↔ entrega).
Feature EPIC 13 — Recompensas & Níveis.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rewards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("icon", sa.String(length=50), nullable=False),
        sa.Column("unlock_type", sa.String(length=20), nullable=False),
        sa.Column("required_level", sa.Integer(), nullable=True),
        sa.Column(
            "required_achievement_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("achievements.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("featured", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
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
            "unlock_type IN ('level', 'achievement')",
            name="ck_reward_unlock_type",
        ),
    )
    op.create_index(
        op.f("ix_rewards_required_achievement_id"),
        "rewards",
        ["required_achievement_id"],
    )
    op.create_index(op.f("ix_rewards_is_active"), "rewards", ["is_active"])

    op.create_table(
        "reward_redemptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "reward_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rewards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "redeemed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "candidate_profile_id",
            "reward_id",
            name="uq_reward_redemption_profile_reward",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'fulfilled', 'cancelled')",
            name="ck_reward_redemption_status",
        ),
    )
    op.create_index(
        op.f("ix_reward_redemptions_candidate_profile_id"),
        "reward_redemptions",
        ["candidate_profile_id"],
    )
    op.create_index(
        op.f("ix_reward_redemptions_reward_id"),
        "reward_redemptions",
        ["reward_id"],
    )
    op.create_index(
        op.f("ix_reward_redemptions_status"),
        "reward_redemptions",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reward_redemptions_status"), table_name="reward_redemptions")
    op.drop_index(op.f("ix_reward_redemptions_reward_id"), table_name="reward_redemptions")
    op.drop_index(
        op.f("ix_reward_redemptions_candidate_profile_id"),
        table_name="reward_redemptions",
    )
    op.drop_table("reward_redemptions")

    op.drop_index(op.f("ix_rewards_is_active"), table_name="rewards")
    op.drop_index(op.f("ix_rewards_required_achievement_id"), table_name="rewards")
    op.drop_table("rewards")
