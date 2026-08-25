"""Acesso a dados da entidade `Guardian`.

Isola toda query relacionada a responsáveis — a camada de services nunca
monta SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardian import Guardian


class GuardianRepository:
    """Repositório de leitura/escrita de responsáveis."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, guardian_id: uuid.UUID) -> Guardian | None:
        """Um responsável pelo id."""
        stmt = select(Guardian).where(Guardian.id == guardian_id)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def get_by_confirmation_token(self, token: str) -> Guardian | None:
        """Resolve o responsável pelo link mágico (`/guardian-portal/{token}`).

        É a única forma de acesso do próprio responsável — ele não tem conta
        no app, então posse do token substitui login (mesmo racional de um
        link de reset de senha).
        """
        stmt = select(Guardian).where(Guardian.confirmation_token == token)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def get_primary_for_profile(self, candidate_profile_id: uuid.UUID) -> Guardian | None:
        """O responsável principal do candidato (ou None se nenhum cadastrado)."""
        stmt = select(Guardian).where(
            Guardian.candidate_profile_id == candidate_profile_id,
            Guardian.is_primary.is_(True),
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def list_for_profile(self, candidate_profile_id: uuid.UUID) -> list[Guardian]:
        """Todos os responsáveis do candidato, principal primeiro."""
        stmt = (
            select(Guardian)
            .where(Guardian.candidate_profile_id == candidate_profile_id)
            .order_by(Guardian.is_primary.desc(), Guardian.created_at)
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def map_primary_by_profile_ids(
        self, candidate_profile_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, Guardian]:
        """Responsável principal de vários candidatos de uma vez (evita N+1 no job)."""
        if not candidate_profile_ids:
            return {}
        stmt = select(Guardian).where(
            Guardian.candidate_profile_id.in_(candidate_profile_ids),
            Guardian.is_primary.is_(True),
        )
        rows = (await self._db.execute(stmt)).scalars().all()
        return {guardian.candidate_profile_id: guardian for guardian in rows}

    async def upsert_primary(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        name: str | None,
        phone: str | None,
        email: str | None,
    ) -> Guardian | None:
        """Cria ou atualiza o responsável principal (flush, sem commit).

        Se nenhum responsável existe ainda e os três campos vêm vazios, não
        cria uma linha à toa — `None` sinaliza "sem responsável cadastrado".
        """
        existing = await self.get_primary_for_profile(candidate_profile_id)
        if existing is None:
            if name is None and phone is None and email is None:
                return None
            existing = Guardian(candidate_profile_id=candidate_profile_id, is_primary=True)
            self._db.add(existing)

        existing.name = name
        existing.phone = phone
        existing.email = email
        await self._db.flush()
        return existing
