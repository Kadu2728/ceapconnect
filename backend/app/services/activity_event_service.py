"""Regra de negócio do tracking comportamental (EPIC 14 — fase 2).

Ponto único de entrada para registrar eventos do candidato. As features do
modelo de risco (fase 3) são derivadas exclusivamente deste log.

**Princípio: tracking nunca quebra a experiência do usuário.** `track` é
best-effort — qualquer falha ao registrar é logada e engolida, jamais propaga
para o fluxo de negócio que a chamou (concluir uma missão não pode falhar
porque o log de eventos falhou).

Duas formas de uso, conforme o chamador controle ou não a transação:

- `track(...)`        → participa da transação em curso (não commita). Use
  dentro de um fluxo que já vai commitar (ex.: conclusão de missão).
- `track_committed(...)` → abre e fecha a própria transação. Use em fluxos de
  leitura, onde não há commit natural (ex.: visualizar o Dashboard).
"""

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_event import ActivityEventName
from app.repositories.activity_event_repository import ActivityEventRepository

logger = logging.getLogger("ceap_connect.tracking")


async def track(
    db: AsyncSession,
    *,
    candidate_profile_id: uuid.UUID,
    name: ActivityEventName,
    props: dict[str, Any] | None = None,
) -> None:
    """Registra um evento na transação em curso (não commita). Best-effort."""
    try:
        await ActivityEventRepository(db).create(
            candidate_profile_id=candidate_profile_id, name=name, props=props
        )
    except Exception:  # noqa: BLE001 — tracking jamais quebra o fluxo de negócio
        logger.exception("Falha ao registrar evento %s", name)


async def track_committed(
    db: AsyncSession,
    *,
    candidate_profile_id: uuid.UUID,
    name: ActivityEventName,
    props: dict[str, Any] | None = None,
) -> None:
    """Registra um evento e commita. Best-effort — faz rollback em caso de falha.

    Para fluxos de leitura (GET), onde não existe um commit natural ao qual o
    evento possa se juntar.
    """
    try:
        await ActivityEventRepository(db).create(
            candidate_profile_id=candidate_profile_id, name=name, props=props
        )
        await db.commit()
    except Exception:  # noqa: BLE001 — tracking jamais quebra o fluxo de negócio
        logger.exception("Falha ao registrar evento %s", name)
        await db.rollback()
