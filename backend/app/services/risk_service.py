"""Regra de negócio da Predição de Evasão (EPIC 14 — fase 3).

Orquestra a derivação de features (`risk_feature_service`) e o cálculo do
score (`app.core.risk_scoring.RiskScorer`) para:

1. **Recalcular** o score de todos os candidatos ativos, agrupados por
   coorte (a mediana de progresso só faz sentido dentro da mesma turma) —
   chamado pelo job agendado e pelo endpoint interno de recompute.
2. **Servir a fila** priorizada do Console de Intervenção, sempre filtrada
   pelo escopo de coorte do usuário (`CohortScope` — nunca em memória, sempre
   na query).
3. **Servir o detalhe** de um candidato (score, fatores, timeline, histórico
   de intervenções).
4. **Registrar intervenções** e, 7 dias depois, **medir o impacto** (o score
   caiu? houve atividade?) — fecha o loop que sustenta a métrica de produto
   "risco médio caiu X%".

Depende apenas da interface `RiskScorer` (nunca de `HeuristicRiskScorer`
diretamente) — trocar o modelo de score no futuro é injetar outra
implementação aqui, sem tocar endpoints nem repositórios.
"""

import time
import uuid
from dataclasses import asdict
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.rbac import CohortScope
from app.core.risk_scoring import HeuristicRiskScorer, RiskScorer, RiskTier
from app.models.candidate_profile import CandidateProfile, CandidateStatus
from app.repositories.activity_event_repository import ActivityEventRepository
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.cohort_repository import CohortRepository
from app.repositories.intervention_repository import InterventionRepository
from app.repositories.risk_score_repository import RiskScoreRepository
from app.repositories.silence_signal_repository import SilenceSignalRepository
from app.repositories.user_repository import UserRepository
from app.schemas.risk import (
    ActivityTimelineItem,
    CandidateRiskDetail,
    InterventionCreateRequest,
    InterventionItem,
    RecomputeSummary,
    RiskFactorItem,
    RiskQueueItem,
    RiskQueueResponse,
)
from app.services import journey_service, silence_radar_service
from app.services.risk_feature_service import derive_features_for_group

_RECENT_ACTIVITY_LIMIT = 20
_MEASUREMENT_DELAY_DAYS = 7
# Janela de "entrou em silêncio recentemente" mostrada no Console. Uma semana
# é o horizonte em que a abordagem ainda muda o desfecho — mais que isso e o
# abandono já se consolidou (é a mesma lógica do limiar de silêncio em si).
_NEW_SILENCE_WINDOW_DAYS = 7

# Instância padrão do scorer heurístico. `recompute_all` aceita um `scorer`
# alternativo via parâmetro — é o ponto de troca para um modelo treinado no
# futuro, sem mudar a assinatura pública do service.
_default_scorer: RiskScorer = HeuristicRiskScorer()


async def recompute_all(db: AsyncSession, *, scorer: RiskScorer | None = None) -> RecomputeSummary:
    """Recalcula o score de todos os candidatos ativos e mede intervenções vencidas.

    Agrupa candidatos por `cohort_id` antes de derivar features — a mediana de
    progresso usada em "abaixo da mediana da coorte" só é válida dentro da
    mesma turma. Candidatos sem coorte (`cohort_id is None`) formam seu
    próprio grupo (sem mediana comparável — `below_cohort_median` fica `None`
    para eles).
    """
    active_scorer = scorer or _default_scorer
    started_at = time.monotonic()

    profiles = await CandidateProfileRepository(db).list_active_candidates()
    groups: dict[uuid.UUID | None, list[CandidateProfile]] = {}
    for profile in profiles:
        groups.setdefault(profile.cohort_id, []).append(profile)

    score_repo = RiskScoreRepository(db)
    processed = 0
    silence_signals_opened = 0
    for group in groups.values():
        # Recomputa a etapa da jornada antes de derivar as features — pega
        # avanços de candidatos inativos (ex.: exam_date chegou) que nunca
        # abriram o Dashboard para disparar o sync por lá (ver journey_service).
        await journey_service.sync_group(db, group)
        features_list = await derive_features_for_group(db, group)

        # Radar de Silêncio: reaproveita as features já derivadas acima —
        # detectar a travessia para o silêncio não custa nenhuma query de
        # comportamento nova, e roda na mesma cadência do score porque
        # responde à mesma pergunta ("esta pessoa sumiu?"), só que como
        # evento em vez de estado.
        silence_signals_opened += await silence_radar_service.sync_signals(db, features_list)

        for features in features_list:
            result = active_scorer.score(features)
            factors_payload = [
                {"key": f.key, "label": f.label, "points": round(f.points, 2)}
                for f in result.factors
            ]
            features_payload = _serialize_features(features)
            await score_repo.upsert(
                candidate_profile_id=uuid.UUID(features.candidate_profile_id),
                score=result.score,
                tier=result.tier,
                factors=factors_payload,
                explanation=result.explanation,
                features=features_payload,
                model_version=active_scorer.model_version,
            )
            await score_repo.append_history(
                candidate_profile_id=uuid.UUID(features.candidate_profile_id),
                score=result.score,
                tier=result.tier,
                factors=factors_payload,
                explanation=result.explanation,
                features=features_payload,
                model_version=active_scorer.model_version,
            )
            processed += 1

    await db.commit()

    measured = await _measure_due_interventions(db)
    duration = round(time.monotonic() - started_at, 2)

    return RecomputeSummary(
        candidates_processed=processed,
        interventions_measured=measured,
        duration_seconds=duration,
        silence_signals_opened=silence_signals_opened,
    )


async def get_queue(
    db: AsyncSession,
    scope: CohortScope,
    *,
    cohort_id: uuid.UUID | None = None,
    tier: RiskTier | None = None,
) -> RiskQueueResponse:
    """Fila priorizada por risco, restrita ao escopo de coorte do usuário."""
    if cohort_id is not None and not scope.allows(cohort_id):
        raise ForbiddenException("Você não tem acesso a esta coorte.")

    rows = await RiskScoreRepository(db).list_queue(
        cohort_ids=scope.cohort_ids, tier=tier, cohort_id_filter=cohort_id
    )

    items = [
        RiskQueueItem(
            candidate_profile_id=risk.candidate_profile_id,
            candidate_name=user.name,
            candidate_email=user.email,
            cohort_id=cohort.id if cohort is not None else None,
            cohort_name=cohort.name if cohort is not None else None,
            score=risk.score,
            tier=risk.tier,
            explanation=risk.explanation,
            computed_at=risk.computed_at,
            paused_until=pause.ends_at if pause is not None else None,
            silence_detected_at=silence.detected_at if silence is not None else None,
        )
        for risk, _profile, user, cohort, pause, silence in rows
    ]

    counts_by_tier = {"baixo": 0, "medio": 0, "alto": 0}
    for item in items:
        counts_by_tier[item.tier] += 1

    new_silence_since = datetime.now(UTC) - timedelta(days=_NEW_SILENCE_WINDOW_DAYS)
    new_silence_count = await SilenceSignalRepository(db).count_detected_since(
        since=new_silence_since
    )

    return RiskQueueResponse(
        items=items,
        total=len(items),
        counts_by_tier=counts_by_tier,
        paused_count=sum(1 for item in items if item.paused_until is not None),
        new_silence_count=new_silence_count,
    )


async def get_candidate_risk(
    db: AsyncSession, scope: CohortScope, candidate_profile_id: uuid.UUID
) -> CandidateRiskDetail:
    """Detalhe de risco de um candidato — 404 se não existir, 403 fora do escopo."""
    profile = await CandidateProfileRepository(db).get_by_id(candidate_profile_id)
    if profile is None:
        raise NotFoundException("Candidato não encontrado.")
    if not scope.allows(profile.cohort_id):
        raise ForbiddenException("Você não tem acesso a este candidato.")

    user = await UserRepository(db).get_by_id(profile.user_id)
    if user is None:
        raise NotFoundException("Candidato não encontrado.")

    cohort_name = None
    if profile.cohort_id is not None:
        cohort = await CohortRepository(db).get_by_id(profile.cohort_id)
        cohort_name = cohort.name if cohort is not None else None

    risk = await RiskScoreRepository(db).get_by_profile_id(candidate_profile_id)

    activity_rows = await ActivityEventRepository(db).list_recent_for_profile(
        candidate_profile_id, limit=_RECENT_ACTIVITY_LIMIT
    )
    recent_activity = [
        ActivityTimelineItem(name=event.name, props=event.props, occurred_at=event.occurred_at)
        for event in activity_rows
    ]

    intervention_rows = await InterventionRepository(db).list_for_candidate(candidate_profile_id)
    interventions = await _to_intervention_items(db, intervention_rows)

    return CandidateRiskDetail(
        candidate_profile_id=candidate_profile_id,
        candidate_name=user.name,
        candidate_email=user.email,
        cohort_id=profile.cohort_id,
        cohort_name=cohort_name,
        status=profile.status,
        status_changed_at=profile.status_changed_at,
        score=risk.score if risk is not None else None,
        tier=risk.tier if risk is not None else None,
        factors=([RiskFactorItem(**factor) for factor in risk.factors] if risk is not None else []),
        explanation=risk.explanation if risk is not None else None,
        computed_at=risk.computed_at if risk is not None else None,
        recent_activity=recent_activity,
        interventions=interventions,
    )


async def update_candidate_status(
    db: AsyncSession,
    scope: CohortScope,
    candidate_profile_id: uuid.UUID,
    status: CandidateStatus,
) -> CandidateProfile:
    """Registra o outcome real do candidato — rótulo manual usado no backtest do modelo de risco.

    Mesma regra de escopo das outras ações do Console de Intervenção: só quem
    tem acesso à coorte do candidato pode mudar. Uma vez fora de `active`, o
    candidato para de entrar no recálculo periódico (`recompute_all`) — o
    último score calculado fica congelado, é ele que vira o rótulo comparado
    ao outcome no backtest.
    """
    profile = await CandidateProfileRepository(db).get_by_id(candidate_profile_id)
    if profile is None:
        raise NotFoundException("Candidato não encontrado.")
    if not scope.allows(profile.cohort_id):
        raise ForbiddenException("Você não tem acesso a este candidato.")

    updated = await CandidateProfileRepository(db).update_status(
        profile, status=status, changed_at=datetime.now(UTC)
    )
    await db.commit()
    return updated


async def create_intervention(
    db: AsyncSession, scope: CohortScope, payload: InterventionCreateRequest
) -> InterventionItem:
    """Registra uma intervenção, capturando o score atual do candidato.

    O score no momento do contato (`score_at_creation`) é a base de comparação
    da medição de impacto — por isso a intervenção só pode ser criada para um
    candidato que já tem score calculado.
    """
    profile = await CandidateProfileRepository(db).get_by_id(payload.candidate_profile_id)
    if profile is None:
        raise NotFoundException("Candidato não encontrado.")
    if not scope.allows(profile.cohort_id):
        raise ForbiddenException("Você não tem acesso a este candidato.")

    risk = await RiskScoreRepository(db).get_by_profile_id(payload.candidate_profile_id)
    if risk is None:
        raise NotFoundException("Este candidato ainda não tem score de risco calculado.")

    intervention = await InterventionRepository(db).create(
        candidate_profile_id=payload.candidate_profile_id,
        created_by_user_id=scope.user.id,
        channel=payload.channel,
        outcome=payload.outcome,
        notes=payload.notes,
        score_at_creation=risk.score,
    )
    await db.commit()

    items = await _to_intervention_items(db, [intervention])
    return items[0]


async def _measure_due_interventions(db: AsyncSession) -> int:
    """Mede o impacto de intervenções feitas há 7+ dias e ainda não medidas.

    Compara o score atual ao score no momento do contato e verifica se houve
    qualquer `ActivityEvent` do candidato depois da intervenção — os dois
    sinais que respondem "funcionou?" sem exigir um pipeline de report à parte.
    """
    threshold = datetime.now(UTC) - timedelta(days=_MEASUREMENT_DELAY_DAYS)
    intervention_repo = InterventionRepository(db)
    due = await intervention_repo.list_due_for_measurement(before=threshold)
    if not due:
        return 0

    score_repo = RiskScoreRepository(db)
    activity_repo = ActivityEventRepository(db)
    now = datetime.now(UTC)

    for intervention in due:
        current_risk = await score_repo.get_by_profile_id(intervention.candidate_profile_id)
        score_after = (
            current_risk.score if current_risk is not None else intervention.score_at_creation
        )

        last_activity_at = await activity_repo.get_last_occurred_at(
            intervention.candidate_profile_id
        )
        had_activity_after = (
            last_activity_at is not None and last_activity_at > intervention.created_at
        )

        await intervention_repo.mark_measured(
            intervention,
            measured_at=now,
            score_after=score_after,
            had_activity_after=had_activity_after,
        )

    await db.commit()
    return len(due)


async def _to_intervention_items(db: AsyncSession, interventions: list) -> list[InterventionItem]:
    """Projeta `Intervention` no schema de API, resolvendo o nome de quem registrou.

    Resolve todos os autores em uma única query (`UserRepository.get_by_ids`)
    — nunca um `get_by_id` por intervenção dentro do loop (N+1 corrigido na
    Fase 4 — otimizações medidas).
    """
    creator_ids = {
        intervention.created_by_user_id
        for intervention in interventions
        if intervention.created_by_user_id is not None
    }
    creators = await UserRepository(db).get_by_ids(list(creator_ids))
    creator_name_by_id = {creator.id: creator.name for creator in creators}

    return [
        InterventionItem(
            id=intervention.id,
            channel=intervention.channel,
            outcome=intervention.outcome,
            notes=intervention.notes,
            created_by_name=(
                creator_name_by_id.get(intervention.created_by_user_id)
                if intervention.created_by_user_id is not None
                else None
            ),
            score_at_creation=intervention.score_at_creation,
            created_at=intervention.created_at,
            measured_at=intervention.measured_at,
            score_after=intervention.score_after,
            had_activity_after=intervention.had_activity_after,
        )
        for intervention in interventions
    ]


def _serialize_features(features) -> dict:  # noqa: ANN001 — dataclass genérico local
    """Serializa `CandidateRiskFeatures` para JSONB (snapshot de auditoria)."""
    return asdict(features)
