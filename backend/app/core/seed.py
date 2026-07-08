"""Seed idempotente dos catálogos do Dashboard (EPIC 03).

Popula `JourneyStep`, `Mission`, `Achievement` e `Event` com dados
representativos, caso ainda não existam — nunca duplica em reexecuções
(cada catálogo é checado por sua chave natural: `key`/`title`/`name`).

Uso:
    python -m app.core.seed

Não é uma migration: migrations do Alembic cuidam apenas do *schema*
(estrutura das tabelas); este script cuida dos *dados* de catálogo, que
podem evoluir de forma independente do schema (ex.: adicionar uma nova
missão não exige alterar nenhuma coluna).
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.achievement import Achievement
from app.models.event import Event
from app.models.journey_step import JourneyStep
from app.models.mission import Mission

logger = logging.getLogger("ceap_connect.seed")
logging.basicConfig(level=logging.INFO)

_JOURNEY_STEPS: tuple[dict, ...] = (
    {
        "key": "inscricao",
        "label": "Inscrição",
        "description": "Cadastro realizado e conta criada na plataforma.",
        "order": 1,
    },
    {
        "key": "documentacao",
        "label": "Documentação",
        "description": "Envio e validação dos documentos exigidos no edital.",
        "order": 2,
    },
    {
        "key": "confirmacao",
        "label": "Confirmação",
        "description": "Inscrição confirmada após validação da documentação.",
        "order": 3,
    },
    {
        "key": "preparacao",
        "label": "Preparação",
        "description": "Período de estudos e acompanhamento das missões e eventos.",
        "order": 4,
    },
    {
        "key": "dia_da_prova",
        "label": "Dia da prova",
        "description": "Realização da prova do processo seletivo.",
        "order": 5,
    },
    {
        "key": "resultado",
        "label": "Resultado",
        "description": "Divulgação do resultado final do processo seletivo.",
        "order": 6,
    },
)

_MISSIONS: tuple[dict, ...] = (
    {
        "title": "Conheça o CEAP",
        "description": "Explore a plataforma e conheça a estrutura do CEAP Connect.",
        "xp_reward": 20,
        "due_date": None,
    },
    {
        "title": "Assista ao vídeo institucional",
        "description": "Assista ao vídeo de apresentação do processo seletivo.",
        "xp_reward": 30,
        "due_date": None,
    },
    {
        "title": "Confirme sua documentação",
        "description": "Envie e confirme os documentos exigidos no edital.",
        "xp_reward": 50,
        "due_date": None,
    },
    {
        "title": "Responda o quiz de ambientação",
        "description": "Responda o quiz rápido sobre como funciona a jornada.",
        "xp_reward": 25,
        "due_date": None,
    },
)

_ACHIEVEMENTS: tuple[dict, ...] = (
    {
        "name": "Primeira Missão",
        "description": "Concluiu a primeira missão da jornada.",
        "icon": "flag",
    },
    {
        "name": "100 XP",
        "description": "Acumulou 100 pontos de experiência.",
        "icon": "zap",
    },
    {
        "name": "Perfil Completo",
        "description": "Completou 100% dos dados do perfil.",
        "icon": "badge-check",
    },
)


def _future_events(now: datetime) -> tuple[dict, ...]:
    """Monta os eventos de seed com datas relativas a `now` (sempre futuras)."""
    return (
        {
            "title": "Palestra: Como se preparar para a prova do CEAP",
            "description": "Dicas práticas de estudo e gestão do tempo com especialistas do CEAP.",
            "date": now + timedelta(days=14),
            "location": "Auditório Central do CEAP",
            "image_url": None,
        },
        {
            "title": "Encontro de boas-vindas dos candidatos",
            "description": "Roda de conversa para os candidatos se conhecerem e tirarem dúvidas.",
            "date": now + timedelta(days=21),
            "location": "Online — transmissão ao vivo",
            "image_url": None,
        },
        {
            "title": "Simulado presencial CEAP Connect",
            "description": "Simulado completo nas mesmas condições do dia da prova oficial.",
            "date": now + timedelta(days=45),
            "location": "Unidade CEAP — Sede",
            "image_url": None,
        },
    )


async def _seed_journey_steps(db: AsyncSession) -> int:
    existing = {row.key for row in (await db.execute(select(JourneyStep.key))).all()}
    to_create = [JourneyStep(**data) for data in _JOURNEY_STEPS if data["key"] not in existing]
    db.add_all(to_create)
    return len(to_create)


async def _seed_missions(db: AsyncSession) -> int:
    existing = {row.title for row in (await db.execute(select(Mission.title))).all()}
    to_create = [Mission(**data) for data in _MISSIONS if data["title"] not in existing]
    db.add_all(to_create)
    return len(to_create)


async def _seed_achievements(db: AsyncSession) -> int:
    existing = {row.name for row in (await db.execute(select(Achievement.name))).all()}
    to_create = [Achievement(**data) for data in _ACHIEVEMENTS if data["name"] not in existing]
    db.add_all(to_create)
    return len(to_create)


async def _seed_events(db: AsyncSession) -> int:
    existing = {row.title for row in (await db.execute(select(Event.title))).all()}
    to_create = [
        Event(**data) for data in _future_events(datetime.now(UTC)) if data["title"] not in existing
    ]
    db.add_all(to_create)
    return len(to_create)


async def seed() -> None:
    """Executa o seed completo, numa única transação idempotente."""
    async with AsyncSessionLocal() as db:
        created_steps = await _seed_journey_steps(db)
        created_missions = await _seed_missions(db)
        created_achievements = await _seed_achievements(db)
        created_events = await _seed_events(db)
        await db.commit()

    logger.info(
        "Seed concluído: %d etapas, %d missões, %d conquistas, %d eventos criados.",
        created_steps,
        created_missions,
        created_achievements,
        created_events,
    )


async def _main() -> None:
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(_main())
