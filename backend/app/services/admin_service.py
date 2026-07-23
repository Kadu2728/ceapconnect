"""Regra de negócio do painel administrativo (EPIC 10 + EPIC 13).

Orquestra o `AdminRepository` para a visão geral de métricas (somente leitura) e
gerencia a fila de resgates de recompensas (listar + confirmar entrega). O
controle de acesso (apenas admins) é feito na dependency `get_current_admin`,
não aqui.
"""

import uuid
from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.gamification import LEVEL_TIERS, resolve_level
from app.models.reward_redemption import STATUS_FULFILLED
from app.repositories.admin_repository import AdminRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.reward_repository import RewardRedemptionRepository
from app.schemas.admin import (
    AdminOverview,
    AdminRedemptionItem,
    AdminRedemptionListResponse,
    DailyCount,
    LevelBucket,
    TopReward,
)

_SIGNUPS_WINDOW_DAYS = 14
_TOP_REWARDS_LIMIT = 5


async def get_overview(db: AsyncSession) -> AdminOverview:
    """Monta o agregado de métricas da plataforma para o painel admin."""
    repo = AdminRepository(db)
    now = datetime.now(UTC)

    total = await repo.count_students()
    accessed = await repo.count_students_accessed()
    never_accessed = total - accessed
    engagement_rate = round((accessed / total) * 100, 1) if total > 0 else 0.0

    active_24h = await repo.count_students_active_since(now - timedelta(days=1))
    active_7d = await repo.count_students_active_since(now - timedelta(days=7))
    active_30d = await repo.count_students_active_since(now - timedelta(days=30))

    new_7d = await repo.count_students_registered_since(now - timedelta(days=7))
    new_30d = await repo.count_students_registered_since(now - timedelta(days=30))

    missions_completed = await repo.count_missions_completed()
    event_registrations = await repo.count_event_registrations()

    achievements_unlocked = await repo.count_achievements_unlocked()
    total_xp = await repo.total_xp_distributed()
    avg_xp = round(total_xp / total) if total > 0 else 0
    rewards_redeemed = await repo.count_redemptions()
    rewards_pending = await repo.count_pending_redemptions()
    rewards_fulfilled = await repo.count_fulfilled_redemptions()

    student_xp = await repo.list_student_xp()
    level_distribution = _build_level_distribution(student_xp)

    top_rewards = [
        TopReward(title=title, provider=provider, count=count)
        for title, provider, count in await repo.top_redeemed_rewards(limit=_TOP_REWARDS_LIMIT)
    ]

    signups = await repo.signups_by_day(now - timedelta(days=_SIGNUPS_WINDOW_DAYS))
    signups_daily = [DailyCount(date=day, count=count) for day, count in signups]

    return AdminOverview(
        total_students=total,
        accessed=accessed,
        never_accessed=never_accessed,
        engagement_rate=engagement_rate,
        active_24h=active_24h,
        active_7d=active_7d,
        active_30d=active_30d,
        new_7d=new_7d,
        new_30d=new_30d,
        missions_completed=missions_completed,
        event_registrations=event_registrations,
        achievements_unlocked=achievements_unlocked,
        total_xp=total_xp,
        avg_xp=avg_xp,
        rewards_redeemed=rewards_redeemed,
        rewards_pending=rewards_pending,
        rewards_fulfilled=rewards_fulfilled,
        level_distribution=level_distribution,
        top_rewards=top_rewards,
        signups_daily=signups_daily,
    )


def _build_level_distribution(student_xp: list[int]) -> list[LevelBucket]:
    """Conta quantos alunos estão em cada nível, incluindo níveis com zero.

    Sempre retorna todas as faixas (mesmo vazias) para o gráfico manter forma
    estável entre atualizações.
    """
    counts = Counter(resolve_level(xp).level for xp in student_xp)
    return [
        LevelBucket(level=tier.level, name=tier.name, count=counts.get(tier.level, 0))
        for tier in LEVEL_TIERS
    ]


async def list_redemptions(db: AsyncSession) -> AdminRedemptionListResponse:
    """Lista todos os resgates de recompensas (fila de entrega), mais recentes primeiro."""
    rows = await RewardRedemptionRepository(db).list_all_detailed()

    items = [
        AdminRedemptionItem(
            id=redemption.id,
            student_name=user.name,
            student_email=user.email,
            reward_title=reward.title,
            reward_provider=reward.provider,
            status=redemption.status,
            redeemed_at=redemption.redeemed_at,
            fulfilled_at=redemption.fulfilled_at,
        )
        for redemption, reward, user in rows
    ]

    pending = sum(1 for item in items if item.status == "pending")
    fulfilled = sum(1 for item in items if item.status == "fulfilled")
    return AdminRedemptionListResponse(
        redemptions=items,
        pending_count=pending,
        fulfilled_count=fulfilled,
    )


async def fulfill_redemption(db: AsyncSession, redemption_id: uuid.UUID) -> AdminRedemptionItem:
    """Confirma a entrega de um resgate e notifica o aluno. Idempotência via 409.

    Regras:
    - o resgate precisa existir (404);
    - um resgate já entregue não pode ser entregue de novo (409).
    """
    redemption_repo = RewardRedemptionRepository(db)
    detailed = await redemption_repo.get_detailed_by_id(redemption_id)
    if detailed is None:
        raise NotFoundException("Resgate não encontrado.")
    redemption, reward, user = detailed
    if redemption.status == STATUS_FULFILLED:
        raise ConflictException("Este resgate já foi marcado como entregue.")

    redemption.status = STATUS_FULFILLED
    redemption.fulfilled_at = datetime.now(UTC)
    await db.flush()

    await NotificationRepository(db).create(
        candidate_profile_id=redemption.candidate_profile_id,
        title="Recompensa entregue ✅",
        description=(
            f'Sua recompensa "{reward.title}" foi liberada pela equipe do CEAP. '
            "Confira os detalhes de acesso enviados a você."
        ),
        category="sistema",
    )
    await db.commit()

    return AdminRedemptionItem(
        id=redemption.id,
        student_name=user.name,
        student_email=user.email,
        reward_title=reward.title,
        reward_provider=reward.provider,
        status=redemption.status,
        redeemed_at=redemption.redeemed_at,
        fulfilled_at=redemption.fulfilled_at,
    )
