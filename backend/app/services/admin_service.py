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

from app.core import cache
from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException
from app.core.gamification import LEVEL_TIERS, resolve_level
from app.models.reward_redemption import STATUS_FULFILLED
from app.repositories.admin_repository import AdminRepository
from app.repositories.reward_repository import RewardRedemptionRepository
from app.schemas.admin import (
    AdminOverview,
    AdminRedemptionItem,
    AdminRedemptionListResponse,
    DailyCount,
    InterventionImpact,
    LevelBucket,
    TopReward,
)
from app.services import notification_service

_SIGNUPS_WINDOW_DAYS = 14
_TOP_REWARDS_LIMIT = 5
_INTERVENTION_IMPACT_WINDOW_DAYS = 30

# "v1": versiona a chave, não o valor — um deploy que mude o formato de
# `AdminOverview` vira uma chave nova em vez de tentar (e falhar) desserializar
# um JSON velho. Cache é só um acelerador (ver app.core.cache); nunca há um
# "invalidar na escrita" aqui de propósito — o overview é lido por poucos
# admins/coordenadores, TTL curto já resolve staleness sem espalhar lógica de
# invalidação pelos vários services que alteram os dados agregados.
_OVERVIEW_CACHE_KEY = "admin:overview:v1"


async def get_overview(db: AsyncSession) -> AdminOverview:
    """Monta o agregado de métricas da plataforma para o painel admin.

    Cacheado por `settings.admin_overview_cache_ttl_seconds` (Fase 4 —
    otimizações medidas): o endpoint dispara ~18 queries agregadas sobre a
    base inteira, caro para uma tela de métricas de staff que tolera folga.
    """
    cached = await cache.get_cached(_OVERVIEW_CACHE_KEY)
    if cached is not None:
        return AdminOverview.model_validate_json(cached)

    overview = await _build_overview(db)

    await cache.set_cached(
        _OVERVIEW_CACHE_KEY,
        overview.model_dump_json(),
        ttl_seconds=settings.admin_overview_cache_ttl_seconds,
    )
    return overview


async def _build_overview(db: AsyncSession) -> AdminOverview:
    """Monta o agregado a partir do banco — sempre a fonte de verdade, cache à parte."""
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

    intervention_impact = await _build_intervention_impact(repo, now)

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
        intervention_impact=intervention_impact,
    )


async def _build_intervention_impact(repo: AdminRepository, now: datetime) -> InterventionImpact:
    """Monta o card de impacto das intervenções (últimos 30 dias).

    Percentuais são calculados aqui (não em SQL) para evitar divisão por zero
    quando ainda não há nenhuma intervenção medida — nesse caso ficam `None`,
    e o frontend mostra um estado de "ainda sem dados" em vez de "0%".
    """
    since = now - timedelta(days=_INTERVENTION_IMPACT_WINDOW_DAYS)
    total, measured, improved, avg_delta, had_activity = await repo.intervention_impact_stats(
        since=since
    )

    pct_improved = round((improved / measured) * 100, 1) if measured > 0 else None
    pct_had_activity = round((had_activity / measured) * 100, 1) if measured > 0 else None

    return InterventionImpact(
        total=total,
        measured=measured,
        pending_measurement=total - measured,
        avg_score_delta=round(avg_delta, 1) if avg_delta is not None else None,
        pct_improved=pct_improved,
        pct_had_activity_after=pct_had_activity,
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

    await notification_service.create_notification(
        db,
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
