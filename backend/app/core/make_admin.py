"""Promove um usuário existente a administrador, pelo e-mail.

Uso:
    python -m app.core.make_admin <email>

O acesso admin nunca é concedido por endpoint público — apenas por este
script operacional, executado por quem tem acesso ao servidor.
"""

import asyncio
import sys

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.models.user import User


async def promote(email: str) -> int:
    normalized = email.strip().lower()
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == normalized))).scalar_one_or_none()

        if user is None:
            print(f"Usuário não encontrado: {normalized}")
            return 1

        if user.is_admin:
            print(f"{normalized} já é admin.")
            return 0

        user.is_admin = True
        await db.commit()
        print(f"OK: {normalized} agora é administrador.")
        return 0


async def _main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python -m app.core.make_admin <email>")
        return 2
    try:
        return await promote(sys.argv[1])
    finally:
        await engine.dispose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
