"""Acesso a dados das entidades `Achievement` e `CandidateAchievement` (EPIC 03/06).

Isola toda query relacionada a conquistas — a camada de services nunca deve
montar SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.models.candidate_achievement import CandidateAchievement


class AchievementRepository:
    """Repositório de leitura de conquistas desbloqueadas por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_recent_for_profile(
        self, candidate_profile_id: uuid.UUID, *, limit: int = 5
    ) -> list[tuple[CandidateAchievement, Achievement]]:
        """Retorna as conquistas mais recentes do candidato, mais recentes primeiro."""
        stmt = (
            select(CandidateAchievement, Achievement)
            .join(Achievement, Achievement.id == CandidateAchievement.achievement_id)
            .where(CandidateAchievement.candidate_profile_id == candidate_profile_id)
            .order_by(CandidateAchievement.unlocked_at.desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def list_all_with_status_for_profile(
        self, candidate_profile_id: uuid.UUID
    ) -> list[tuple[Achievement, CandidateAchievement | None]]:
        """Retorna todo o catálogo de conquistas com o status do candidato.

        `CandidateAchievement` vem preenchido quando a conquista já foi
        desbloqueada e `None` caso contrário (LEFT JOIN). Desbloqueadas
        primeiro (mais recentes no topo), depois as bloqueadas.
        """
        stmt = (
            select(Achievement, CandidateAchievement)
            .outerjoin(
                CandidateAchievement,
                (CandidateAchievement.achievement_id == Achievement.id)
                & (CandidateAchievement.candidate_profile_id == candidate_profile_id),
            )
            .order_by(
                CandidateAchievement.unlocked_at.is_(None).asc(),
                CandidateAchievement.unlocked_at.desc(),
                Achievement.created_at.asc(),
            )
        )
        result = await self._db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_by_name(self, name: str) -> Achievement | None:
        """Busca uma conquista do catálogo pelo nome (chave natural do seed)."""
        stmt = select(Achievement).where(Achievement.name == name)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def has_for_profile(
        self, *, candidate_profile_id: uuid.UUID, achievement_id: uuid.UUID
    ) -> bool:
        """Indica se o candidato já desbloqueou a conquista informada."""
        stmt = select(CandidateAchievement.id).where(
            CandidateAchievement.candidate_profile_id == candidate_profile_id,
            CandidateAchievement.achievement_id == achievement_id,
        )
        return (await self._db.execute(stmt)).first() is not None

    async def unlock(
        self, *, candidate_profile_id: uuid.UUID, achievement_id: uuid.UUID
    ) -> CandidateAchievement:
        """Registra o desbloqueio de uma conquista (flush, sem commit)."""
        candidate_achievement = CandidateAchievement(
            candidate_profile_id=candidate_profile_id,
            achievement_id=achievement_id,
        )
        self._db.add(candidate_achievement)
        await self._db.flush()
        return candidate_achievement
