"""Acesso a dados das entidades `Reward` e `RewardRedemption` (EPIC 13).

Isola toda query de recompensas e resgates — a camada de services nunca monta
SQL/ORM diretamente. As leituras já trazem, via join, a `Achievement` de
gatilho quando a recompensa é desbloqueada por conquista (evita N+1 ao montar o
rótulo de requisito).
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.models.candidate_profile import CandidateProfile
from app.models.reward import Reward
from app.models.reward_redemption import RewardRedemption
from app.models.user import User


class RewardRepository:
    """Repositório de leitura do catálogo de recompensas."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_active_ordered(self) -> list[tuple[Reward, Achievement | None]]:
        """Recompensas ativas + a conquista de gatilho (quando houver).

        Ordena por destaque, `sort_order` e criação — a mesma ordem usada na
        vitrine do frontend.
        """
        stmt = (
            select(Reward, Achievement)
            .outerjoin(Achievement, Achievement.id == Reward.required_achievement_id)
            .where(Reward.is_active.is_(True))
            .order_by(
                Reward.featured.desc(),
                Reward.sort_order.asc(),
                Reward.created_at.asc(),
            )
        )
        result = await self._db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_by_id(self, reward_id: uuid.UUID) -> Reward | None:
        """Uma recompensa pelo id, independente de estar ativa.

        Usado pelo fluxo admin de entrega: um resgate antigo pode apontar para
        uma recompensa que já foi desativada (`is_active=False`), e ainda assim
        precisa ser exibida/entregue.
        """
        stmt = select(Reward).where(Reward.id == reward_id)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def map_by_required_achievement(self) -> dict[uuid.UUID, Reward]:
        """Recompensas ativas por conquista de gatilho, indexadas por `achievement_id`.

        Usado pela feature de Conquistas para exibir, em cada conquista, a
        recompensa que ela desbloqueia ("conclua → ganhe"). Havendo mais de uma
        recompensa para a mesma conquista, prevalece a de maior prioridade de
        exibição (destaque, `sort_order`).
        """
        stmt = (
            select(Reward)
            .where(
                Reward.is_active.is_(True),
                Reward.unlock_type == "achievement",
                Reward.required_achievement_id.is_not(None),
            )
            .order_by(
                Reward.featured.desc(),
                Reward.sort_order.asc(),
                Reward.created_at.asc(),
            )
        )
        rows = (await self._db.execute(stmt)).scalars().all()
        mapping: dict[uuid.UUID, Reward] = {}
        for reward in rows:
            # Primeira ocorrência vence (já vem ordenada por prioridade).
            if reward.required_achievement_id not in mapping:
                mapping[reward.required_achievement_id] = reward
        return mapping

    async def get_with_achievement(
        self, reward_id: uuid.UUID
    ) -> tuple[Reward, Achievement | None] | None:
        """Uma recompensa ativa pelo id, com sua conquista de gatilho (se houver)."""
        stmt = (
            select(Reward, Achievement)
            .outerjoin(Achievement, Achievement.id == Reward.required_achievement_id)
            .where(Reward.id == reward_id, Reward.is_active.is_(True))
        )
        result = await self._db.execute(stmt)
        row = result.first()
        return (row[0], row[1]) if row is not None else None

    async def list_all_ordered(self) -> list[tuple[Reward, Achievement | None]]:
        """Todas as recompensas (ativas e inativas) + conquista de gatilho — gestão admin.

        Ativas primeiro, depois na mesma ordem da vitrine (destaque, `sort_order`).
        """
        stmt = (
            select(Reward, Achievement)
            .outerjoin(Achievement, Achievement.id == Reward.required_achievement_id)
            .order_by(
                Reward.is_active.desc(),
                Reward.featured.desc(),
                Reward.sort_order.asc(),
                Reward.created_at.asc(),
            )
        )
        result = await self._db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def create(self, **fields) -> Reward:
        """Cria uma recompensa no catálogo (flush, sem commit)."""
        reward = Reward(**fields)
        self._db.add(reward)
        await self._db.flush()
        return reward


class RewardRedemptionRepository:
    """Repositório dos resgates de recompensas por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def map_for_profile(
        self, candidate_profile_id: uuid.UUID
    ) -> dict[uuid.UUID, RewardRedemption]:
        """Resgates do candidato indexados por `reward_id` (para compor a listagem)."""
        stmt = select(RewardRedemption).where(
            RewardRedemption.candidate_profile_id == candidate_profile_id
        )
        rows = (await self._db.execute(stmt)).scalars().all()
        return {row.reward_id: row for row in rows}

    async def get(
        self, *, candidate_profile_id: uuid.UUID, reward_id: uuid.UUID
    ) -> RewardRedemption | None:
        """Resgate específico do candidato para uma recompensa (ou None)."""
        stmt = select(RewardRedemption).where(
            RewardRedemption.candidate_profile_id == candidate_profile_id,
            RewardRedemption.reward_id == reward_id,
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def create(
        self, *, candidate_profile_id: uuid.UUID, reward_id: uuid.UUID
    ) -> RewardRedemption:
        """Registra um resgate (status `pending`). Flush, sem commit."""
        redemption = RewardRedemption(
            candidate_profile_id=candidate_profile_id,
            reward_id=reward_id,
        )
        self._db.add(redemption)
        await self._db.flush()
        return redemption

    async def get_by_id(self, redemption_id: uuid.UUID) -> RewardRedemption | None:
        """Um resgate pelo id (usado pelo fluxo admin de entrega)."""
        stmt = select(RewardRedemption).where(RewardRedemption.id == redemption_id)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def get_detailed_by_id(
        self, redemption_id: uuid.UUID
    ) -> tuple[RewardRedemption, Reward, User] | None:
        """Um resgate pelo id, já com recompensa + aluno (resposta do fluxo admin)."""
        stmt = (
            select(RewardRedemption, Reward, User)
            .join(Reward, Reward.id == RewardRedemption.reward_id)
            .join(
                CandidateProfile,
                CandidateProfile.id == RewardRedemption.candidate_profile_id,
            )
            .join(User, User.id == CandidateProfile.user_id)
            .where(RewardRedemption.id == redemption_id)
        )
        row = (await self._db.execute(stmt)).first()
        return (row[0], row[1], row[2]) if row is not None else None

    async def list_all_detailed(
        self,
    ) -> list[tuple[RewardRedemption, Reward, User]]:
        """Todos os resgates com recompensa + aluno, mais recentes primeiro (admin)."""
        stmt = (
            select(RewardRedemption, Reward, User)
            .join(Reward, Reward.id == RewardRedemption.reward_id)
            .join(
                CandidateProfile,
                CandidateProfile.id == RewardRedemption.candidate_profile_id,
            )
            .join(User, User.id == CandidateProfile.user_id)
            .order_by(RewardRedemption.redeemed_at.desc())
        )
        result = await self._db.execute(stmt)
        return [(row[0], row[1], row[2]) for row in result.all()]
