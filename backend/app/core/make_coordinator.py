"""Promove um usuário a coordenador e o vincula a uma coorte (EPIC 14).

Uso:
    python -m app.core.make_coordinator <email> <ano> <semestre>

Exemplo:
    python -m app.core.make_coordinator ana@ceap.org 2026 1

O papel de coordenador dá acesso ao console de intervenção **restrito às
coortes vinculadas** — por isso a coorte é obrigatória. Assim como o admin,
nunca é concedido por endpoint público: apenas por este script operacional.
"""

import asyncio
import sys

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.models.user import ROLE_COORDINATOR, User
from app.repositories.cohort_repository import CohortRepository


async def promote(email: str, year: int, term: str) -> int:
    normalized = email.strip().lower()

    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == normalized))).scalar_one_or_none()
        if user is None:
            print(f"Usuário não encontrado: {normalized}")
            return 1

        repo = CohortRepository(db)
        cohort = await repo.get_by_year_term(year=year, term=term)
        if cohort is None:
            print(f"Coorte {year}.{term} não encontrada. Rode o seed primeiro.")
            return 1

        if user.role != ROLE_COORDINATOR:
            user.role = ROLE_COORDINATOR

        existing = await repo.list_cohort_ids_for_coordinator(user.id)
        if cohort.id in existing:
            print(f"{normalized} já coordena a coorte {cohort.name}.")
        else:
            await repo.assign_coordinator(user_id=user.id, cohort_id=cohort.id)
            print(f"OK: {normalized} agora coordena {cohort.name}.")

        await db.commit()
        return 0


async def _main() -> int:
    if len(sys.argv) < 4:
        print("Uso: python -m app.core.make_coordinator <email> <ano> <semestre>")
        return 2
    try:
        return await promote(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    except ValueError:
        print("Ano deve ser numérico. Ex.: python -m app.core.make_coordinator a@b.com 2026 1")
        return 2
    finally:
        await engine.dispose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
