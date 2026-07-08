"""Acesso a dados da entidade `CandidateProfile` (EPIC 03 — Dashboard).

Isola toda query relacionada ao perfil de gamificação do candidato — a
camada de services nunca deve montar SQL/ORM diretamente.
"""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import CandidateProfile


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

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        current_journey_step_key: str,
        exam_date: date | None,
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
        )
        self._db.add(profile)
        await self._db.flush()
        return profile
