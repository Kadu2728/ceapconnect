"""Acesso a dados da entidade `CandidateProfile` (EPIC 03 — Dashboard).

Isola toda query relacionada ao perfil de gamificação do candidato — a
camada de services nunca deve montar SQL/ORM diretamente.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import STATUS_ACTIVE, CandidateProfile, CandidateStatus
from app.models.user import ROLE_CANDIDATE, User


class CandidateProfileRepository:
    """Repositório de leitura/escrita da entidade `CandidateProfile`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> CandidateProfile | None:
        """Busca o perfil (ativo, não deletado) associado a um usuário."""
        stmt = select(CandidateProfile).where(
            CandidateProfile.user_id == user_id,
            CandidateProfile.deleted_at.is_(None),
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, profile_id: uuid.UUID) -> CandidateProfile | None:
        """Busca um perfil pelo id (ativo, não deletado)."""
        stmt = select(CandidateProfile).where(
            CandidateProfile.id == profile_id,
            CandidateProfile.deleted_at.is_(None),
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def list_active_candidates(self) -> list[CandidateProfile]:
        """Perfis de candidatos ativos (role=candidate, não deletados,
        `status=active`) — base do recálculo de risco (EPIC 14). Nunca inclui
        coordenadores/admins: risco é uma métrica sobre quem está no processo
        seletivo. Candidatos com outcome já decidido (aprovado/evadido/desistente)
        saem do recálculo — o último score calculado antes da decisão fica
        congelado, é ele que vira o rótulo do backtest.
        """
        stmt = (
            select(CandidateProfile)
            .join(User, User.id == CandidateProfile.user_id)
            .where(
                CandidateProfile.deleted_at.is_(None),
                CandidateProfile.status == STATUS_ACTIVE,
                User.deleted_at.is_(None),
                User.role == ROLE_CANDIDATE,
            )
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def update_status(
        self, profile: CandidateProfile, *, status: CandidateStatus, changed_at: datetime
    ) -> CandidateProfile:
        """Atualiza o outcome do candidato (flush, sem commit) — rótulo manual usado no backtest."""
        profile.status = status
        profile.status_changed_at = changed_at
        await self._db.flush()
        return profile

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        current_journey_step_key: str,
        exam_date: date | None,
        interview_date: date | None = None,
    ) -> CandidateProfile:
        """Adiciona um novo perfil à sessão e faz `flush` (sem commit).

        Ver `UserRepository.create` para o racional de não commitar aqui:
        faz parte da transação orquestrada por
        `app.services.candidate_profile_service.bootstrap_new_candidate`.
        """
        profile = CandidateProfile(
            user_id=user_id,
            current_journey_step_key=current_journey_step_key,
            exam_date=exam_date,
            interview_date=interview_date,
        )
        self._db.add(profile)
        await self._db.flush()
        return profile
