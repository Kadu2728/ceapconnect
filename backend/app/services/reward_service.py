"""Regra de negócio de Recompensas (EPIC 13).

Duas responsabilidades:

1. Listar o catálogo de recompensas com o nível do candidato e o status de cada
   recompensa (bloqueada / disponível / resgatada / entregue) —
   `GET /api/v1/rewards`.
2. Resgatar uma recompensa desbloqueada, gerando o pedido de entrega e uma
   notificação real para o candidato — `POST /api/v1/rewards/{id}/redeem`.

O "desbloqueio" é derivado da progressão (nível a partir do XP **ou** conquista
específica), nunca armazenado de forma redundante: a fonte da verdade é sempre o
XP e as conquistas do candidato. Assim, ajustar a curva de níveis ou o catálogo
recalcula tudo automaticamente, sem dados a migrar.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.gamification import LevelProgress, resolve_level
from app.models.achievement import Achievement
from app.models.reward import Reward
from app.models.reward_redemption import (
    STATUS_CANCELLED,
    STATUS_FULFILLED,
    RewardRedemption,
)
from app.models.user import User
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.reward_repository import (
    RewardRedemptionRepository,
    RewardRepository,
)
from app.schemas.gamification import LevelInfo
from app.schemas.reward import (
    RedeemRewardResponse,
    RewardItem,
    RewardListResponse,
    RewardStatus,
    RewardSummary,
)
from app.services import notification_service
from app.services.candidate_profile_service import get_profile_or_raise


async def list_rewards(db: AsyncSession, user: User) -> RewardListResponse:
    """Catálogo de recompensas com o nível do candidato e o status de cada item."""
    profile = await get_profile_or_raise(db, user)
    level = resolve_level(profile.xp_total)

    rows = await RewardRepository(db).list_active_ordered()
    unlocked_achievement_ids = await AchievementRepository(db).list_unlocked_ids_for_profile(
        profile.id
    )
    redemptions = await RewardRedemptionRepository(db).map_for_profile(profile.id)

    items = [
        _to_item(
            reward,
            achievement,
            level=level,
            unlocked_achievement_ids=unlocked_achievement_ids,
            redemption=redemptions.get(reward.id),
        )
        for reward, achievement in rows
    ]

    unlocked = sum(1 for item in items if item.status != "locked")
    redeemed = sum(1 for item in items if item.status in ("redeemed", "fulfilled"))

    return RewardListResponse(
        level=to_level_info(level),
        rewards=items,
        summary=RewardSummary(total=len(items), unlocked=unlocked, redeemed=redeemed),
    )


async def redeem_reward(db: AsyncSession, user: User, reward_id: uuid.UUID) -> RedeemRewardResponse:
    """Resgata uma recompensa desbloqueada e emite a notificação de confirmação.

    Regras:
    - a recompensa precisa existir e estar ativa (404);
    - a condição de desbloqueio precisa estar atingida (409);
    - uma recompensa já resgatada não pode ser resgatada de novo (409).
    """
    profile = await get_profile_or_raise(db, user)

    row = await RewardRepository(db).get_with_achievement(reward_id)
    if row is None:
        raise NotFoundException("Recompensa não encontrada.")
    reward, achievement = row

    level = resolve_level(profile.xp_total)
    unlocked_achievement_ids = await AchievementRepository(db).list_unlocked_ids_for_profile(
        profile.id
    )
    if not is_reward_unlocked(
        reward, level=level, unlocked_achievement_ids=unlocked_achievement_ids
    ):
        raise ConflictException("Você ainda não desbloqueou esta recompensa.")

    redemption_repo = RewardRedemptionRepository(db)
    existing = await redemption_repo.get(candidate_profile_id=profile.id, reward_id=reward.id)
    if existing is not None and existing.status != STATUS_CANCELLED:
        raise ConflictException("Você já resgatou esta recompensa.")

    redemption = await redemption_repo.create(candidate_profile_id=profile.id, reward_id=reward.id)
    await notification_service.create_notification(
        db,
        candidate_profile_id=profile.id,
        title="Recompensa resgatada 🎉",
        description=(
            f'Você resgatou "{reward.title}". Nossa equipe vai entrar em contato '
            "com os próximos passos para você receber."
        ),
        category="sistema",
    )
    await db.commit()

    item = _to_item(
        reward,
        achievement,
        level=level,
        unlocked_achievement_ids=unlocked_achievement_ids,
        redemption=redemption,
    )
    return RedeemRewardResponse(reward=item)


def is_reward_unlocked(
    reward: Reward,
    *,
    level: LevelProgress,
    unlocked_achievement_ids: set[uuid.UUID],
) -> bool:
    """Avalia se a condição de desbloqueio da recompensa foi atingida.

    Público: reutilizado pelo Dashboard para escolher a "próxima recompensa"
    em destaque sem duplicar a regra de desbloqueio.
    """
    if reward.unlock_type == "level":
        return reward.required_level is not None and level.level >= reward.required_level
    # unlock_type == "achievement"
    return (
        reward.required_achievement_id is not None
        and reward.required_achievement_id in unlocked_achievement_ids
    )


def _resolve_status(*, unlocked: bool, redemption: RewardRedemption | None) -> RewardStatus:
    """Deriva o status da recompensa para o candidato (resgate > desbloqueio)."""
    if redemption is not None and redemption.status != STATUS_CANCELLED:
        return "fulfilled" if redemption.status == STATUS_FULFILLED else "redeemed"
    return "available" if unlocked else "locked"


def reward_requirement_label(reward: Reward, achievement: Achievement | None) -> str:
    """Texto legível do requisito de desbloqueio, pronto para a UI."""
    if reward.unlock_type == "level":
        return f"Alcance o Nível {reward.required_level}"
    if achievement is not None:
        return f'Desbloqueie a conquista "{achievement.name}"'
    return "Requisito indisponível"


def _to_item(
    reward: Reward,
    achievement: Achievement | None,
    *,
    level: LevelProgress,
    unlocked_achievement_ids: set[uuid.UUID],
    redemption: RewardRedemption | None,
) -> RewardItem:
    """Compõe `Reward` (catálogo) + progressão do candidato num item de API."""
    unlocked = is_reward_unlocked(
        reward, level=level, unlocked_achievement_ids=unlocked_achievement_ids
    )
    return RewardItem(
        id=reward.id,
        title=reward.title,
        description=reward.description,
        provider=reward.provider,
        category=reward.category,
        icon=reward.icon,
        featured=reward.featured,
        unlock_type=reward.unlock_type,
        required_level=reward.required_level,
        requirement_label=reward_requirement_label(reward, achievement),
        status=_resolve_status(unlocked=unlocked, redemption=redemption),
        redeemed_at=redemption.redeemed_at if redemption is not None else None,
        fulfilled_at=redemption.fulfilled_at if redemption is not None else None,
    )


def to_level_info(level: LevelProgress) -> LevelInfo:
    """Projeta o `LevelProgress` de domínio no schema de API `LevelInfo`.

    Público: reutilizado pelo Dashboard, que também expõe o nível do candidato.
    """
    return LevelInfo(
        level=level.level,
        name=level.name,
        xp_total=level.xp_total,
        current_level_xp=level.current_level_xp,
        next_level_xp=level.next_level_xp,
        xp_into_level=level.xp_into_level,
        xp_to_next=level.xp_to_next,
        progress_percentage=level.progress_percentage,
        is_max_level=level.is_max_level,
    )
