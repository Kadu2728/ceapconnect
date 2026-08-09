"""Backfill único: calcula `interview_date` para perfis criados antes da
EPIC 17 (Envolver o responsável) existir, quando `bootstrap_new_candidate`
ainda não preenchia esse campo.

Mesma regra usada em candidatos novos: `exam_date + interview_offset_days`.
Perfis sem `exam_date` (não deveria acontecer, mas defensivo) são pulados.

Uso: python -m app.core.backfill_interview_dates
"""

import asyncio
from datetime import timedelta

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.candidate_profile import CandidateProfile


async def backfill() -> None:
    async with AsyncSessionLocal() as db:
        stmt = select(CandidateProfile).where(
            CandidateProfile.deleted_at.is_(None),
            CandidateProfile.interview_date.is_(None),
        )
        profiles = (await db.execute(stmt)).scalars().all()

        backfilled = 0
        skipped = 0
        for profile in profiles:
            if profile.exam_date is None:
                skipped += 1
                continue
            profile.interview_date = profile.exam_date + timedelta(
                days=settings.interview_offset_days
            )
            backfilled += 1

        await db.commit()
        print(
            f"Concluído. {backfilled} perfil(is) atualizado(s), "
            f"{skipped} pulado(s) sem exam_date, de {len(profiles)} pendente(s)."
        )


if __name__ == "__main__":
    asyncio.run(backfill())
