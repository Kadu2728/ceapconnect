"""Regra de negócio de Missões (EPIC 05).

Lista as missões do candidato (com progresso) e conclui uma missão —
concessão de XP e desbloqueio de conquistas acontecem aqui, numa única
transação atômica. Nenhuma query é montada diretamente: tudo passa pelos
repositórios.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.mission import Mission
from app.models.mission_progress import STATUS_COMPLETED, MissionProgress
from app.models.user import User
from app.repositories.mission_repository import MissionProgressRepository, MissionRepository
from app.schemas.mission import (
    CompleteMissionResponse,
    MissionItem,
    MissionListResponse,
    MissionSummary,
    UnlockedAchievement,
)
from app.services import achievement_service
from app.services.candidate_profile_service import get_profile_or_raise


async def list_missions(db: AsyncSession, user: User) -> MissionListResponse:
    """Retorna as missões do candidato (pendentes primeiro) com o resumo de progresso."""
    profile = await get_profile_or_raise(db, user)
    rows = await MissionRepository(db).list_with_progress_for_profile(profile.id)

    missions = [_to_item(mission, progress) for mission, progress in rows]
    completed = sum(1 for item in missions if item.status == STATUS_COMPLETED)

    return MissionListResponse(
        missions=missions,
        summary=MissionSummary(
            total=len(missions),
            completed=completed,
            xp_total=profile.xp_total,
        ),
    )


async def complete_mission(
    db: AsyncSession, user: User, mission_id: uuid.UUID
) -> CompleteMissionResponse:
    """Conclui uma missão pendente do candidato, concede XP e avalia conquistas.

    Regras:
    - a missão precisa existir e pertencer ao progresso do candidato (404);
    - uma missão já concluída não pode ser concluída de novo (409 — idempotência
      explícita, evita XP duplicado).
    """
    profile = await get_profile_or_raise(db, user)
    progress_repo = MissionProgressRepository(db)

    progress = await progress_repo.get_by_profile_and_mission(
        candidate_profile_id=profile.id, mission_id=mission_id
    )
    if progress is None:
        raise NotFoundException("Missão não encontrada para este candidato.")
    if progress.status == STATUS_COMPLETED:
        raise ConflictException("Esta missão já foi concluída.")

    mission = await MissionRepository(db).get_by_id(mission_id)
    if mission is None:
        raise NotFoundException("Missão não encontrada.")

    progress.status = STATUS_COMPLETED
    progress.completed_at = datetime.now(UTC)
    profile.xp_total += mission.xp_reward
    await db.flush()

    completed_count = await progress_repo.count_completed_for_profile(profile.id)
    newly_unlocked = await achievement_service.evaluate_mission_achievements(
        db, profile, completed_missions=completed_count, xp_total=profile.xp_total
    )

    await db.commit()

    return CompleteMissionResponse(
        mission=_to_item(mission, progress),
        xp_gained=mission.xp_reward,
        xp_total=profile.xp_total,
        unlocked_achievements=[
            UnlockedAchievement.model_validate(achievement) for achievement in newly_unlocked
        ],
    )


def _to_item(mission: Mission, progress: MissionProgress) -> MissionItem:
    """Combina `Mission` (catálogo) + `MissionProgress` (candidato) num item de API."""
    return MissionItem(
        id=mission.id,
        title=mission.title,
        description=mission.description,
        xp_reward=mission.xp_reward,
        due_date=mission.due_date,
        status=progress.status,
        completed_at=progress.completed_at,
    )
