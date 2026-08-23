"""Regra de negócio de Conquistas (EPIC 06).

Duas responsabilidades:

1. Listar o catálogo de conquistas com o status (desbloqueada ou não) do
   candidato — consumido por `GET /api/v1/achievements`.
2. Avaliar e desbloquear conquistas como efeito colateral da conclusão de uma
   missão — chamado por `mission_service`, dentro da mesma transação.

As regras referenciam as conquistas do catálogo pelo nome (chave natural do
seed). Se uma conquista esperada não existir (catálogo não semeado), a regra
simplesmente não desbloqueia nada, em vez de quebrar.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.models.candidate_profile import CandidateProfile
from app.models.reward import Reward
from app.models.user import User
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.reward_repository import RewardRepository
from app.schemas.achievement import (
    AchievementItem,
    AchievementListResponse,
    AchievementReward,
    AchievementSummary,
)
from app.services.candidate_profile_service import get_profile_or_raise

_ACHIEVEMENT_FIRST_MISSION = "Primeira Missão"
_ACHIEVEMENT_100_XP = "100 XP"
_ACHIEVEMENT_PROFILE_COMPLETE = "Perfil Completo"
_ACHIEVEMENT_GUARDIAN_TRAINING = "Responsável na Jornada"
_XP_MILESTONE = 100


async def list_achievements(db: AsyncSession, user: User) -> AchievementListResponse:
    """Retorna o catálogo de conquistas com o status de desbloqueio do candidato."""
    profile = await get_profile_or_raise(db, user)
    rows = await AchievementRepository(db).list_all_with_status_for_profile(profile.id)
    rewards_by_achievement = await RewardRepository(db).map_by_required_achievement()

    items = [
        AchievementItem(
            id=achievement.id,
            name=achievement.name,
            description=achievement.description,
            icon=achievement.icon,
            unlocked=candidate_achievement is not None,
            unlocked_at=(
                candidate_achievement.unlocked_at if candidate_achievement is not None else None
            ),
            reward=_reward_for(rewards_by_achievement.get(achievement.id)),
        )
        for achievement, candidate_achievement in rows
    ]

    unlocked = sum(1 for item in items if item.unlocked)
    return AchievementListResponse(
        achievements=items,
        summary=AchievementSummary(total=len(items), unlocked=unlocked),
    )


def _reward_for(reward: Reward | None) -> AchievementReward | None:
    """Projeta a recompensa atrelada a uma conquista (ou None) no schema de API."""
    if reward is None:
        return None
    return AchievementReward(id=reward.id, title=reward.title, provider=reward.provider)


async def evaluate_mission_achievements(
    db: AsyncSession,
    profile: CandidateProfile,
    *,
    completed_missions: int,
    xp_total: int,
) -> list[Achievement]:
    """Desbloqueia as conquistas cujas condições foram atingidas. Não commita.

    Idempotente: conquistas já desbloqueadas não são registradas de novo.
    """
    repo = AchievementRepository(db)
    newly_unlocked: list[Achievement] = []

    if completed_missions >= 1:
        unlocked = await _unlock_if_absent(repo, profile, _ACHIEVEMENT_FIRST_MISSION)
        if unlocked is not None:
            newly_unlocked.append(unlocked)

    if xp_total >= _XP_MILESTONE:
        unlocked = await _unlock_if_absent(repo, profile, _ACHIEVEMENT_100_XP)
        if unlocked is not None:
            newly_unlocked.append(unlocked)

    return newly_unlocked


async def unlock_profile_complete(
    db: AsyncSession, profile: CandidateProfile
) -> Achievement | None:
    """Desbloqueia "Perfil Completo" quando o candidato salva o perfil. Não commita.

    Idempotente: se já estiver desbloqueada (ou o catálogo não a tiver), não faz
    nada. Chamado por `profile_service` dentro da mesma transação.
    """
    return await _unlock_if_absent(
        AchievementRepository(db), profile, _ACHIEVEMENT_PROFILE_COMPLETE
    )


async def unlock_guardian_training(
    db: AsyncSession, profile: CandidateProfile
) -> Achievement | None:
    """Desbloqueia "Responsável na Jornada" quando o responsável conclui a formação.

    Nunca concede XP — é um marco do responsável, não uma ação do candidato
    (ver `app.models.guardian`, módulo docstring). Não commita; chamado por
    `app.services.guardian_service.mark_training_attended` na mesma transação.
    """
    return await _unlock_if_absent(
        AchievementRepository(db), profile, _ACHIEVEMENT_GUARDIAN_TRAINING
    )


async def _unlock_if_absent(
    repo: AchievementRepository, profile: CandidateProfile, name: str
) -> Achievement | None:
    """Desbloqueia a conquista de nome `name` se existir e ainda não estiver desbloqueada."""
    achievement = await repo.get_by_name(name)
    if achievement is None:
        return None

    already = await repo.has_for_profile(
        candidate_profile_id=profile.id, achievement_id=achievement.id
    )
    if already:
        return None

    await repo.unlock(candidate_profile_id=profile.id, achievement_id=achievement.id)
    return achievement
