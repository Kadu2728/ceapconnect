"""Regra de negócio da Tela de Perfil (EPIC 09).

Compõe os dados cadastrais do usuário com um resumo de gamificação (nível, XP e
contadores) e permite editar os campos livres (nome e telefone). Salvar o perfil
também desbloqueia a conquista "Perfil Completo" (antes inalcançável), fechando
mais um laço da gamificação.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.gamification import resolve_level
from app.models.candidate_profile import CandidateProfile
from app.models.reward_redemption import STATUS_CANCELLED
from app.models.user import User
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.mission_repository import MissionProgressRepository
from app.repositories.reward_repository import RewardRedemptionRepository
from app.schemas.profile import (
    GuardianEmailNoticeResult,
    ProfileResponse,
    ProfileStats,
    ProfileUpdateRequest,
)
from app.services import achievement_service, guardian_notice_service, reward_service
from app.services.candidate_profile_service import get_profile_or_raise


async def get_profile(db: AsyncSession, user: User) -> ProfileResponse:
    """Monta o perfil do candidato com dados cadastrais + resumo de gamificação."""
    profile = await get_profile_or_raise(db, user)
    return await _build_response(db, user, profile)


async def update_profile(
    db: AsyncSession, user: User, payload: ProfileUpdateRequest
) -> ProfileResponse:
    """Atualiza dados do candidato e do responsável, e desbloqueia "Perfil Completo"."""
    profile = await get_profile_or_raise(db, user)

    user.name = payload.name
    user.phone = payload.phone

    # Se o e-mail do responsável mudou, o último aviso enviado não vale mais
    # para o contato novo — evita mostrar "avisado" para um e-mail errado.
    if payload.guardian_email != profile.guardian_email:
        profile.guardian_notified_at = None

    profile.guardian_name = payload.guardian_name
    profile.guardian_phone = payload.guardian_phone
    profile.guardian_email = payload.guardian_email
    await db.flush()

    await achievement_service.unlock_profile_complete(db, profile)
    await db.commit()

    return await _build_response(db, user, profile)


async def notify_guardian_email(db: AsyncSession, user: User) -> GuardianEmailNoticeResult:
    """Envia o e-mail de aviso da entrevista ao responsável (EPIC 17)."""
    profile = await get_profile_or_raise(db, user)

    sent, message = await guardian_notice_service.send_guardian_email(user=user, profile=profile)
    if sent:
        profile.guardian_notified_at = datetime.now(UTC)
        await db.commit()

    return GuardianEmailNoticeResult(
        sent=sent, message=message, guardian_notified_at=profile.guardian_notified_at
    )


async def _build_response(
    db: AsyncSession, user: User, profile: CandidateProfile
) -> ProfileResponse:
    """Compõe o payload de perfil (dados + estatísticas de gamificação)."""
    level = resolve_level(profile.xp_total)

    missions_completed = await MissionProgressRepository(db).count_completed_for_profile(profile.id)
    achievements_unlocked = len(
        await AchievementRepository(db).list_unlocked_ids_for_profile(profile.id)
    )
    redemptions = await RewardRedemptionRepository(db).map_for_profile(profile.id)
    rewards_redeemed = sum(
        1 for redemption in redemptions.values() if redemption.status != STATUS_CANCELLED
    )

    return ProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        cpf_masked=_mask_cpf(user.cpf),
        phone=user.phone,
        member_since=user.created_at,
        stats=ProfileStats(
            level=reward_service.to_level_info(level),
            missions_completed=missions_completed,
            achievements_unlocked=achievements_unlocked,
            rewards_redeemed=rewards_redeemed,
        ),
        interview_date=profile.interview_date,
        interview_location=settings.interview_location,
        guardian_name=profile.guardian_name,
        guardian_phone=profile.guardian_phone,
        guardian_email=profile.guardian_email,
        guardian_notified_at=profile.guardian_notified_at,
    )


def _mask_cpf(cpf: str) -> str:
    """Mascara o CPF, revelando só os 3 primeiros e os 2 últimos dígitos."""
    digits = "".join(ch for ch in cpf if ch.isdigit())
    if len(digits) != 11:
        return "***"
    return f"{digits[:3]}.***.***-{digits[9:]}"
