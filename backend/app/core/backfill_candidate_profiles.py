"""Backfill único: cria `CandidateProfile` para usuários registrados antes
da EPIC 03 (Dashboard) existir, quando `bootstrap_new_candidate` ainda não
rodava no cadastro.

Uso: python -m app.core.backfill_candidate_profiles
"""

import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.services.candidate_profile_service import bootstrap_new_candidate


async def backfill() -> None:
    async with AsyncSessionLocal() as db:
        users = (await db.execute(select(User).where(User.deleted_at.is_(None)))).scalars().all()
        profile_repo = CandidateProfileRepository(db)

        backfilled = 0
        for user in users:
            existing = await profile_repo.get_by_user_id(user.id)
            if existing is not None:
                continue
            await bootstrap_new_candidate(db, user.id)
            backfilled += 1
            print(f"Perfil criado para {user.email}")

        await db.commit()
        print(f"Concluído. {backfilled} perfil(is) criado(s) de {len(users)} usuário(s).")


if __name__ == "__main__":
    asyncio.run(backfill())
