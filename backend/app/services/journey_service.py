"""Avanço de etapa da jornada (KPI de conversão inscrição→prova).

Até esta feature, `CandidateProfile.current_journey_step_key` era escrito
**uma única vez**, no cadastro, e nunca mais atualizado — nenhum candidato
avançava de etapa de verdade, o que tornava impossível medir conversão entre
etapas (o funil não tinha dado nenhum para mostrar).

`current_journey_step_key` passa a ser tratado como valor **derivado**:
`sync_group`/`sync_one` recomputam a etapa real a partir de sinais concretos
— nunca confiam cegamente na coluna, que existe só como cache para leituras
rápidas (ex.: `risk_feature_service`, que lê muitos perfis de uma vez).

Critério de avanço por etapa (todos automáticos, sem ação manual):
1. Inscrição — sempre satisfeita (perfil só existe após o cadastro).
2-4. Documentação / Confirmação / Preparação — avançam juntas quando os
   `REQUIRED_DOCUMENT_TYPES` (EPIC 15) estão todos enviados. Não existe hoje
   nenhum fluxo de "validação manual da documentação" no produto — inventar
   um gate falso seria pior que admitir que essas três etapas hoje têm o
   mesmo critério real.
5. Dia da prova — quando `exam_date` chega.
6. Resultado — quando o coordenador decide o outcome (`status != active`,
   EPIC 14 fase 2).

Nunca regride: um candidato só avança, mesmo que os sinais mudem para trás
(ex.: `exam_date` reagendada). Cada etapa cruzada emite `step_completed`
(`ActivityEvent`) — é esse rastro, com timestamp real, que alimenta o funil
de conversão inscrição→prova, não a contagem por etapa atual isolada.
"""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_event import EVENT_STEP_COMPLETED
from app.models.candidate_document import REQUIRED_DOCUMENT_TYPES
from app.models.candidate_profile import STATUS_ACTIVE, CandidateProfile
from app.models.journey_step import JourneyStep
from app.repositories.candidate_document_repository import CandidateDocumentRepository
from app.repositories.journey_step_repository import JourneyStepRepository
from app.services import activity_event_service

_REQUIRED_DOCUMENT_COUNT = len(REQUIRED_DOCUMENT_TYPES)

# Ordens do catálogo (`app.core.seed._JOURNEY_STEPS`): 1 inscrição, 2
# documentação, 3 confirmação, 4 preparação, 5 dia da prova, 6 resultado.
_ORDER_DOCUMENTATION_GATE = 4
_ORDER_EXAM_DAY = 5
_ORDER_RESULT = 6


async def sync_one(db: AsyncSession, profile: CandidateProfile) -> bool:
    """Recomputa a etapa de um único candidato. Retorna `True` se avançou."""
    advanced_ids = await sync_group(db, [profile])
    return profile.id in advanced_ids


async def sync_group(db: AsyncSession, profiles: list[CandidateProfile]) -> set[uuid.UUID]:
    """Recomputa a etapa de um grupo de candidatos, em lote (sem N+1).

    Não commita — quem chama controla a transação (mesma convenção de
    `risk_feature_service`/`derive_features_for_group`). Retorna os ids dos
    perfis cuja etapa avançou.
    """
    if not profiles:
        return set()

    profile_ids = [p.id for p in profiles]
    doc_counts = await CandidateDocumentRepository(db).count_by_profile_ids(profile_ids)
    steps = await JourneyStepRepository(db).list_ordered()
    step_by_order = {step.order: step for step in steps}
    step_by_key = {step.key: step for step in steps}
    today = datetime.now(UTC).date()

    advanced: set[uuid.UUID] = set()
    for profile in profiles:
        target_order = _resolve_target_order(profile, doc_counts.get(profile.id, 0), today)
        current_step = step_by_key.get(profile.current_journey_step_key)
        current_order = current_step.order if current_step is not None else 1
        if target_order <= current_order:
            continue

        for order in range(current_order + 1, target_order + 1):
            step = step_by_order.get(order)
            if step is None:
                continue
            await _emit_step_completed(db, profile, step)

        profile.current_journey_step_key = step_by_order[target_order].key
        advanced.add(profile.id)

    if advanced:
        await db.flush()
    return advanced


def _resolve_target_order(
    profile: CandidateProfile, uploaded_document_count: int, today: date
) -> int:
    """A etapa mais avançada que o candidato já satisfaz, avaliada em ordem.

    Sequencial de propósito: um `exam_date` no passado nunca "pula" um
    candidato pra "Dia da prova" se ele ainda não completou a documentação —
    cada gate só é checado depois do anterior estar satisfeito.
    """
    if uploaded_document_count < _REQUIRED_DOCUMENT_COUNT:
        return 1
    if profile.exam_date is None or today < profile.exam_date:
        return _ORDER_DOCUMENTATION_GATE
    if profile.status == STATUS_ACTIVE:
        return _ORDER_EXAM_DAY
    return _ORDER_RESULT


async def _emit_step_completed(
    db: AsyncSession, profile: CandidateProfile, step: JourneyStep
) -> None:
    """Registra a transição no log comportamental — histórico real para o funil."""
    await activity_event_service.track(
        db,
        candidate_profile_id=profile.id,
        name=EVENT_STEP_COMPLETED,
        props={"step_key": step.key},
    )
