"""Acesso a dados de `GuardianCandidateLink` (RBAC do responsável).

Isola a query que sustenta o escopo relacional do responsável — a camada de
services/scope nunca monta SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardian_candidate_link import (
    AUTHORIZED_CONSENT_STATUSES,
    CONSENT_PENDING,
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

    async def list_for_candidate(
        self, candidate_profile_id: uuid.UUID
    ) -> list[GuardianCandidateLink]:
        """Todos os vínculos de responsáveis pedindo/tendo acesso a este
        candidato — base da tela de consentimento (fase C do RBAC do
        responsável)."""
        stmt = select(GuardianCandidateLink).where(
            GuardianCandidateLink.candidate_profile_id == candidate_profile_id
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def count_pending_for_guardian(self, guardian_user_id: uuid.UUID) -> int:
        """Quantos vínculos deste responsável ainda aguardam o candidato
        consentir — só a contagem (fase C: usada para explicar uma lista de
        filhos vazia sem revelar identidade antes do consentimento)."""
        stmt = select(func.count()).where(
            GuardianCandidateLink.guardian_user_id == guardian_user_id,
            GuardianCandidateLink.consent_status == CONSENT_PENDING,
        )
        return (await self._db.execute(stmt)).scalar_one()

    async def get_by_id(self, link_id: uuid.UUID) -> GuardianCandidateLink | None:
        stmt = select(GuardianCandidateLink).where(GuardianCandidateLink.id == link_id)
        return (await self._db.execute(stmt)).scalar_one_or_none()

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
