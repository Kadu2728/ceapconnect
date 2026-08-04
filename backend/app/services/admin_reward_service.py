"""Regra de negócio do CRUD de recompensas no admin (EPIC 13 — gestão).

Dá ao CEAP autonomia para criar/editar/ativar recompensas pelo painel. Somente
admins (garantido na dependency `get_current_admin`). A avaliação de desbloqueio
e o resgate continuam em `reward_service` — aqui é só administração do catálogo.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.reward import Reward
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.reward_repository import RewardRepository
from app.schemas.admin_reward import (
    AdminAchievementOption,
    AdminRewardItem,
    AdminRewardListResponse,
    AdminRewardWrite,
)

_EDITABLE_FIELDS = (
    "title",
    "description",
    "provider",
    "category",
    "icon",
    "unlock_type",
    "required_level",
    "required_achievement_id",
    "featured",
    "is_active",
    "sort_order",
)


async def list_rewards(db: AsyncSession) -> AdminRewardListResponse:
    """Lista todas as recompensas (ativas e inativas) + conquistas para o seletor."""
    rows = await RewardRepository(db).list_all_ordered()
    achievements = await AchievementRepository(db).list_all()

    return AdminRewardListResponse(
        rewards=[_to_item(reward, achievement) for reward, achievement in rows],
        achievements=[
            AdminAchievementOption(id=achievement.id, name=achievement.name)
            for achievement in achievements
        ],
    )


async def create_reward(db: AsyncSession, payload: AdminRewardWrite) -> AdminRewardItem:
    """Cria uma recompensa no catálogo."""
    await _ensure_achievement_exists(db, payload)

    fields = {field: getattr(payload, field) for field in _EDITABLE_FIELDS}
    reward = await RewardRepository(db).create(**fields)
    await db.commit()

    achievement_name = await _achievement_name(db, reward.required_achievement_id)
    return _to_item(reward, achievement=None, achievement_name=achievement_name)


async def update_reward(
    db: AsyncSession, reward_id: uuid.UUID, payload: AdminRewardWrite
) -> AdminRewardItem:
    """Atualiza uma recompensa existente (404 se não existir)."""
    reward = await RewardRepository(db).get_by_id(reward_id)
    if reward is None:
        raise NotFoundException("Recompensa não encontrada.")

    await _ensure_achievement_exists(db, payload)

    for field in _EDITABLE_FIELDS:
        setattr(reward, field, getattr(payload, field))
    await db.commit()

    achievement_name = await _achievement_name(db, reward.required_achievement_id)
    return _to_item(reward, achievement=None, achievement_name=achievement_name)


async def _ensure_achievement_exists(db: AsyncSession, payload: AdminRewardWrite) -> None:
    """Valida que a conquista de gatilho existe (quando `unlock_type=achievement`)."""
    if payload.unlock_type != "achievement":
        return
    achievement = await AchievementRepository(db).get_by_id(payload.required_achievement_id)
    if achievement is None:
        raise BadRequestException("Conquista de gatilho não encontrada.")


async def _achievement_name(db: AsyncSession, achievement_id: uuid.UUID | None) -> str | None:
    """Nome da conquista de gatilho (para exibição), quando houver."""
    if achievement_id is None:
        return None
    achievement = await AchievementRepository(db).get_by_id(achievement_id)
    return achievement.name if achievement is not None else None


def _to_item(
    reward: Reward,
    achievement=None,
    *,
    achievement_name: str | None = None,
) -> AdminRewardItem:
    """Projeta uma `Reward` (+ nome da conquista) no schema de gestão."""
    name = achievement.name if achievement is not None else achievement_name
    return AdminRewardItem(
        id=reward.id,
        title=reward.title,
        description=reward.description,
        provider=reward.provider,
        category=reward.category,
        icon=reward.icon,
        unlock_type=reward.unlock_type,
        required_level=reward.required_level,
        required_achievement_id=reward.required_achievement_id,
        required_achievement_name=name,
        featured=reward.featured,
        is_active=reward.is_active,
        sort_order=reward.sort_order,
    )
