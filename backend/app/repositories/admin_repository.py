"""Acesso a dados agregados para o painel administrativo (EPIC 10).

Concentra as queries de contagem/métrica usadas pelo dashboard admin. Métricas
de "alunos" excluem contas administrativas (`is_admin`) e deletadas.
"""

from datetime import date, datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_achievement import CandidateAchievement
from app.models.candidate_profile import CandidateProfile
from app.models.event_registration import EventRegistration
from app.models.mission_progress import STATUS_COMPLETED, MissionProgress
from app.models.reward import Reward
from app.models.reward_redemption import (
    STATUS_FULFILLED,
    STATUS_PENDING,
    RewardRedemption,
)
from app.models.user import User


def _students() -> Select:
    """Filtro base de 'alunos': usuários ativos, não deletados e não admins."""
    return select(User).where(User.deleted_at.is_(None), User.is_admin.is_(False))


def _student_profiles() -> Select:
    """Perfis de candidato pertencentes a alunos (exclui admins/deletados)."""
    return (
        select(CandidateProfile)
        .join(User, User.id == CandidateProfile.user_id)
        .where(User.deleted_at.is_(None), User.is_admin.is_(False))
    )


class AdminRepository:
    """Repositório de leitura de métricas agregadas da plataforma."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _count(self, stmt: Select) -> int:
        count_stmt = select(func.count()).select_from(stmt.subquery())
        return int((await self._db.execute(count_stmt)).scalar_one())

    async def count_students(self) -> int:
        return await self._count(_students())

    async def count_students_accessed(self) -> int:
        """Alunos que já acessaram ao menos uma vez (`last_login_at` preenchido)."""
        return await self._count(_students().where(User.last_login_at.is_not(None)))

    async def count_students_active_since(self, cutoff: datetime) -> int:
        """Alunos com login a partir de `cutoff`."""
        return await self._count(_students().where(User.last_login_at >= cutoff))

    async def count_students_registered_since(self, cutoff: datetime) -> int:
        """Alunos cadastrados a partir de `cutoff`."""
        return await self._count(_students().where(User.created_at >= cutoff))

    async def count_missions_completed(self) -> int:
        stmt = select(MissionProgress).where(MissionProgress.status == STATUS_COMPLETED)
        return await self._count(stmt)

    async def count_event_registrations(self) -> int:
        return await self._count(select(EventRegistration))

    async def count_achievements_unlocked(self) -> int:
        """Total de conquistas desbloqueadas por alunos."""
        stmt = (
            select(CandidateAchievement)
            .join(
                CandidateProfile,
                CandidateProfile.id == CandidateAchievement.candidate_profile_id,
            )
            .join(User, User.id == CandidateProfile.user_id)
            .where(User.deleted_at.is_(None), User.is_admin.is_(False))
        )
        return await self._count(stmt)

    async def total_xp_distributed(self) -> int:
        """Soma do XP acumulado por todos os alunos."""
        stmt = (
            select(func.coalesce(func.sum(CandidateProfile.xp_total), 0))
            .select_from(CandidateProfile)
            .join(User, User.id == CandidateProfile.user_id)
            .where(User.deleted_at.is_(None), User.is_admin.is_(False))
        )
        return int((await self._db.execute(stmt)).scalar_one())

    async def list_student_xp(self) -> list[int]:
        """XP total de cada aluno — para compor a distribuição de níveis no service."""
        stmt = _student_profiles().with_only_columns(CandidateProfile.xp_total)
        rows = (await self._db.execute(stmt)).scalars().all()
        return [int(xp) for xp in rows]

    async def count_redemptions(self) -> int:
        """Total de recompensas resgatadas (todos os status)."""
        return await self._count(select(RewardRedemption))

    async def count_redemptions_by_status(self, status: str) -> int:
        """Recompensas resgatadas num status específico (pending/fulfilled)."""
        return await self._count(select(RewardRedemption).where(RewardRedemption.status == status))

    async def count_pending_redemptions(self) -> int:
        return await self.count_redemptions_by_status(STATUS_PENDING)

    async def count_fulfilled_redemptions(self) -> int:
        return await self.count_redemptions_by_status(STATUS_FULFILLED)

    async def top_redeemed_rewards(self, *, limit: int = 5) -> list[tuple[str, str, int]]:
        """Ranking das recompensas mais resgatadas: (título, instituição, total)."""
        total = func.count(RewardRedemption.id).label("total")
        stmt = (
            select(Reward.title, Reward.provider, total)
            .join(Reward, Reward.id == RewardRedemption.reward_id)
            .group_by(Reward.title, Reward.provider)
            .order_by(total.desc())
            .limit(limit)
        )
        rows = (await self._db.execute(stmt)).all()
        return [(row.title, row.provider, int(row.total)) for row in rows]

    async def signups_by_day(self, since: datetime) -> list[tuple[date, int]]:
        """Cadastros de alunos por dia, a partir de `since` (para o gráfico)."""
        day = func.date(User.created_at).label("day")
        stmt = (
            select(day, func.count().label("total"))
            .where(
                User.deleted_at.is_(None),
                User.is_admin.is_(False),
                User.created_at >= since,
            )
            .group_by(day)
            .order_by(day)
        )
        rows = (await self._db.execute(stmt)).all()
        return [(row.day, int(row.total)) for row in rows]
