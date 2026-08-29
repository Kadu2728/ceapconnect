"""Acesso a dados de `GuardianCandidateLink` (RBAC do responsável).

Isola a query que sustenta o escopo relacional do responsável — a camada de
services/scope nunca monta SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardian_candidate_link import (
    AUTHORIZED_CONSENT_STATUSES,
    ConsentStatus,
    GuardianCandidateLink,
)


class GuardianCandidateLinkRepository:
    """Repositório de leitura/escrita dos vínculos responsável↔candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_authorized_candidate_ids(self, guardian_user_id: uuid.UUID) -> list[uuid.UUID]:
        """Candidatos que este responsável pode ver agora (consentimento em dia).

        Base do `GuardianScope` — filtro sempre na query, nunca em memória:
        um responsável não deve sequer conseguir enumerar um candidato fora
        deste conjunto.
        """
        stmt = select(GuardianCandidateLink.candidate_profile_id).where(
            GuardianCandidateLink.guardian_user_id == guardian_user_id,
            GuardianCandidateLink.consent_status.in_(AUTHORIZED_CONSENT_STATUSES),
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def list_for_guardian(self, guardian_user_id: uuid.UUID) -> list[GuardianCandidateLink]:
        """Todos os vínculos do responsável, inclusive os ainda `pending`/`revoked`
        — usado pela própria tela dele ("aguardando consentimento de...")."""
        stmt = select(GuardianCandidateLink).where(
            GuardianCandidateLink.guardian_user_id == guardian_user_id
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def get(
        self, *, guardian_user_id: uuid.UUID, candidate_profile_id: uuid.UUID
    ) -> GuardianCandidateLink | None:
        stmt = select(GuardianCandidateLink).where(
            GuardianCandidateLink.guardian_user_id == guardian_user_id,
            GuardianCandidateLink.candidate_profile_id == candidate_profile_id,
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def create(
        self,
        *,
        guardian_user_id: uuid.UUID,
        candidate_profile_id: uuid.UUID,
        consent_status: ConsentStatus,
    ) -> GuardianCandidateLink:
        """Cria o vínculo (flush, sem commit — quem chama controla a transação)."""
        link = GuardianCandidateLink(
            guardian_user_id=guardian_user_id,
            candidate_profile_id=candidate_profile_id,
            consent_status=consent_status,
        )
        self._db.add(link)
        await self._db.flush()
        return link
