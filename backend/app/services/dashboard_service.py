"""Regra de negócio do agregado do Dashboard (EPIC 03).

Orquestra os repositórios de cada entidade (jornada, missões, conquistas,
eventos, notificações) para montar o payload único consumido por
`GET /api/v1/dashboard`. Nenhuma query é feita diretamente aqui — tudo passa
pelos repositórios específicos de cada entidade.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.journey_step import JourneyStep
from app.models.user import User
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.event_repository import EventRepository
from app.repositories.journey_step_repository import JourneyStepRepository
from app.repositories.mission_repository import MissionRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.dashboard import (
    DashboardResponse,
    JourneyProgress,
    JourneyStepItem,
    NextMission,
    RecentAchievement,
    UpcomingEvent,
)

_RECENT_ACHIEVEMENTS_LIMIT = 5
_UPCOMING_EVENTS_LIMIT = 5


async def get_dashboard(db: AsyncSession, user: User) -> DashboardResponse:
    """Monta o agregado completo do Dashboard para o usuário autenticado."""
    profile = await CandidateProfileRepository(db).get_by_user_id(user.id)
    if profile is None:
        # Não deve ocorrer em condições normais: todo `User` ganha um
        # `CandidateProfile` no registro (ver `auth_service.register_user`).
        raise NotFoundException("Perfil do candidato não encontrado.")

    steps = await JourneyStepRepository(db).list_ordered()
    journey = _build_journey_progress(steps, profile.current_journey_step_key)

    next_mission_row = await MissionRepository(db).get_next_pending_for_profile(profile.id)
    next_mission = (
        NextMission.model_validate(next_mission_row[0]) if next_mission_row is not None else None
    )

    recent_achievements_rows = await AchievementRepository(db).list_recent_for_profile(
        profile.id, limit=_RECENT_ACHIEVEMENTS_LIMIT
    )
    recent_achievements = [
        RecentAchievement(
            id=achievement.id,
            name=achievement.name,
            description=achievement.description,
            icon=achievement.icon,
            unlocked_at=candidate_achievement.unlocked_at,
        )
        for candidate_achievement, achievement in recent_achievements_rows
    ]

    upcoming_events = [
        UpcomingEvent(id=event.id, title=event.title, date=event.date, location=event.location)
        for event in await EventRepository(db).list_upcoming(limit=_UPCOMING_EVENTS_LIMIT)
    ]

    unread_notifications_count = await NotificationRepository(db).count_unread_for_profile(
        profile.id
    )

    return DashboardResponse(
        greeting_name=_first_name(user.name),
        journey=journey,
        xp_total=profile.xp_total,
        next_mission=next_mission,
        recent_achievements=recent_achievements,
        upcoming_events=upcoming_events,
        unread_notifications_count=unread_notifications_count,
        exam_date=profile.exam_date,
    )


def _build_journey_progress(steps: list[JourneyStep], current_step_key: str) -> JourneyProgress:
    """Calcula o percentual de progresso e o status de cada etapa da jornada."""
    total_steps = len(steps)
    current_step = next((step for step in steps if step.key == current_step_key), None)

    # Defensivo: se a etapa atual do candidato não estiver (mais) no
    # catálogo, trata como 0% em vez de quebrar o Dashboard.
    current_order = current_step.order if current_step is not None else 0
    percentage = round((current_order / total_steps) * 100) if total_steps else 0

    step_items = [
        JourneyStepItem(
            key=step.key,
            label=step.label,
            status=(
                "completed"
                if step.order < current_order
                else "current"
                if step.order == current_order
                else "pending"
            ),
        )
        for step in steps
    ]

    return JourneyProgress(
        percentage=percentage,
        current_step_key=current_step_key,
        steps=step_items,
    )


def _first_name(full_name: str) -> str:
    """Extrai o primeiro nome para uma saudação mais pessoal no Dashboard."""
    return full_name.strip().split(" ")[0] if full_name.strip() else full_name
