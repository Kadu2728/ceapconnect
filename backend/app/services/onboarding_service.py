"""Regra de negócio do onboarding do primeiro login (EPIC 12 — UX).

Marca que o candidato concluiu a tela de boas-vindas. Idempotente: chamar de
novo não altera a data já registrada.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.candidate_profile_service import get_profile_or_raise


async def complete(db: AsyncSession, user: User) -> None:
    """Registra a conclusão do onboarding (uma única vez) e commita."""
    profile = await get_profile_or_raise(db, user)
    if profile.onboarded_at is None:
        profile.onboarded_at = datetime.now(UTC)
        await db.commit()
