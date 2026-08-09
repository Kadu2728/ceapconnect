"""Acesso a dados da entidade `PushSubscription` (EPIC 18 — PWA + push).

Isola toda query relacionada a inscrições de push — a camada de services
nunca deve montar SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.push_subscription import PushSubscription


class PushSubscriptionRepository:
    """Repositório de leitura/escrita de inscrições de push por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def upsert(
        self, *, candidate_profile_id: uuid.UUID, endpoint: str, p256dh: str, auth: str
    ) -> None:
        """Cria a inscrição ou atualiza as chaves se o endpoint já existir
        (o mesmo navegador pode reinscrever com chaves novas)."""
        stmt = (
            pg_insert(PushSubscription)
            .values(
                candidate_profile_id=candidate_profile_id,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth,
            )
            .on_conflict_do_update(
                index_elements=[PushSubscription.endpoint],
                set_={
                    "candidate_profile_id": candidate_profile_id,
                    "p256dh": p256dh,
                    "auth": auth,
                },
            )
        )
        await self._db.execute(stmt)
        await self._db.flush()

    async def delete_by_endpoint(self, *, candidate_profile_id: uuid.UUID, endpoint: str) -> None:
        """Remove a inscrição do candidato (idempotente — não erra se não existir)."""
        stmt = delete(PushSubscription).where(
            PushSubscription.candidate_profile_id == candidate_profile_id,
            PushSubscription.endpoint == endpoint,
        )
        await self._db.execute(stmt)
        await self._db.flush()

    async def delete_by_endpoint_only(self, endpoint: str) -> None:
        """Remove uma inscrição pelo endpoint, sem checar o dono.

        Usado quando o próprio provedor de push informa que o endpoint expirou
        (410 Gone) — nesse ponto não há um `User` autenticado no contexto.
        """
        stmt = delete(PushSubscription).where(PushSubscription.endpoint == endpoint)
        await self._db.execute(stmt)

    async def list_for_profile(self, candidate_profile_id: uuid.UUID) -> list[PushSubscription]:
        """Todas as inscrições ativas do candidato (um por dispositivo)."""
        stmt = select(PushSubscription).where(
            PushSubscription.candidate_profile_id == candidate_profile_id
        )
        return list((await self._db.execute(stmt)).scalars().all())
