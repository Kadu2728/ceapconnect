"""Derivação de features de risco a partir do log de eventos (EPIC 14 — fase 3).

Converte o log bruto de `activity_events` + progresso de missões em
`CandidateRiskFeatures` (ver `app.core.risk_scoring`) — a ponte entre "o que o
candidato fez" e "o que o score precisa saber". Nenhuma regra de pontuação
mora aqui; isso é `risk_scoring.py`.

**Desenhado para lote, nunca para 1 candidato por vez**: todas as leituras são
queries agregadas (`map_*`) sobre a lista inteira de perfis recebida — o job
de recálculo percorre potencialmente milhares de candidatos e uma query por
candidato inviabilizaria o job (é exatamente o full-scan que o índice
`(candidate_profile_id, occurred_at)` foi criado para evitar).

A mediana de progresso da coorte é calculada aqui, no grupo recebido — por
isso `risk_service.py` sempre chama esta função com candidatos de uma mesma
coorte de cada vez (ver `risk_service.recompute_all`).
"""

import statistics
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.risk_scoring import CandidateRiskFeatures
from app.models.activity_event import EVENT_MISSION_ABANDONED
from app.models.candidate_profile import CandidateProfile
from app.repositories.activity_event_repository import ActivityEventRepository
from app.repositories.cohort_repository import CohortRepository
from app.repositories.guardian_repository import GuardianRepository
from app.repositories.journey_step_repository import JourneyStepRepository
from app.repositories.mission_repository import MissionProgressRepository, MissionRepository

# Etapas que exigem uma ação do próprio candidato para avançar (upload de
# documento). É nelas que "estar parado há dias" é um sinal real de risco —
# nas demais etapas, ficar dias sem progredir pode só significar que o
# candidato está esperando uma ação da equipe (ex.: agendamento da prova).
BLOCKING_STEP_KEYS: frozenset[str] = frozenset({"documentacao"})

# Dias na mesma etapa bloqueante antes de considerar o candidato "travado".
STUCK_THRESHOLD_DAYS: float = 5.0


async def derive_features_for_group(
    db: AsyncSession, profiles: list[CandidateProfile]
) -> list[CandidateRiskFeatures]:
    """Deriva as features de risco de um grupo de candidatos (idealmente uma coorte).

    A mediana de conclusão de missões (`below_cohort_median`) é calculada
    dentro deste grupo — passar candidatos de coortes diferentes juntos
    misturaria a mediana entre turmas distintas, então `risk_service.py`
    sempre agrupa por coorte antes de chamar esta função.
    """
    if not profiles:
        return []

    profile_ids = [p.id for p in profiles]
    now = datetime.now(UTC)

    activity_repo = ActivityEventRepository(db)
    last_activity_map = await activity_repo.map_last_occurred_at(profile_ids)
    abandoned_map = await activity_repo.map_event_count_by_name(
        profile_ids, name=EVENT_MISSION_ABANDONED
    )
    completion_ts_map = await activity_repo.map_completion_timestamps(profile_ids)
    first_step_viewed_map = await activity_repo.map_first_step_viewed_at(profile_ids)
    uploaded_doc_set = await activity_repo.set_profiles_with_document_uploaded(profile_ids)

    completed_map = await MissionProgressRepository(db).map_completed_count_for_profiles(
        profile_ids
    )
    total_missions = await MissionRepository(db).count_all()

    journey_steps = await JourneyStepRepository(db).list_ordered()
    step_label_by_key = {step.key: step.label for step in journey_steps}

    guardian_map = await GuardianRepository(db).map_primary_by_profile_ids(profile_ids)
    # Todos os perfis do grupo compartilham a mesma coorte (garantido por
    # `risk_service.recompute_all`), então a data da formação é lida uma
    # única vez, nunca por candidato.
    guardian_training_date = None
    group_cohort_id = profiles[0].cohort_id
    if group_cohort_id is not None:
        cohort = await CohortRepository(db).get_by_id(group_cohort_id)
        guardian_training_date = cohort.guardian_training_date if cohort is not None else None
    today = now.date()

    completion_ratio_by_profile = {
        profile.id: (completed_map.get(profile.id, 0) / total_missions if total_missions else 0.0)
        for profile in profiles
    }
    ratio_values = list(completion_ratio_by_profile.values())
    # Mediana só faz sentido com ao menos 2 candidatos no grupo.
    median_ratio = statistics.median(ratio_values) if len(ratio_values) >= 2 else None

    features: list[CandidateRiskFeatures] = []
    for profile in profiles:
        last_activity = last_activity_map.get(profile.id)
        # Sem nenhum evento registrado: usa a data de cadastro como referência
        # (ver docstring do campo em `CandidateRiskFeatures`).
        reference_dt = last_activity or profile.created_at
        days_since_last_activity = max(0.0, (now - reference_dt).total_seconds() / 86400)

        completion_ratio = completion_ratio_by_profile[profile.id]
        avg_pace = _average_gap_days(completion_ts_map.get(profile.id, []))

        current_key = profile.current_journey_step_key
        current_label = step_label_by_key.get(current_key, current_key)

        is_blocking_step = current_key in BLOCKING_STEP_KEYS
        first_viewed_current_step = first_step_viewed_map.get((profile.id, current_key))
        days_on_current_step = (
            (now - first_viewed_current_step).total_seconds() / 86400
            if first_viewed_current_step is not None
            else 0.0
        )
        has_uploaded_document = profile.id in uploaded_doc_set
        is_stuck = (
            is_blocking_step
            and days_on_current_step >= STUCK_THRESHOLD_DAYS
            and not has_uploaded_document
        )

        below_cohort_median = completion_ratio < median_ratio if median_ratio is not None else None

        guardian = guardian_map.get(profile.id)
        guardian_has_contact = guardian is not None and bool(guardian.phone or guardian.email)
        guardian_training_attended = (
            guardian is not None and guardian.training_attended_at is not None
        )
        guardian_training_overdue = (
            guardian_training_date is not None
            and today > guardian_training_date
            and not guardian_training_attended
        )

        features.append(
            CandidateRiskFeatures(
                candidate_profile_id=str(profile.id),
                days_since_last_activity=days_since_last_activity,
                mission_completion_ratio=completion_ratio,
                missions_abandoned_count=abandoned_map.get(profile.id, 0),
                avg_days_between_completions=avg_pace,
                is_stuck_on_blocking_step=is_stuck,
                current_step_key=current_key,
                current_step_label=current_label,
                below_cohort_median=below_cohort_median,
                cohort_median_completion_ratio=median_ratio,
                guardian_has_contact=guardian_has_contact,
                guardian_training_attended=guardian_training_attended,
                guardian_training_overdue=guardian_training_overdue,
            )
        )

    return features


def _average_gap_days(timestamps: list[datetime]) -> float | None:
    """Média de dias entre timestamps consecutivos. None com menos de 2 pontos."""
    if len(timestamps) < 2:
        return None
    deltas = [
        (timestamps[i] - timestamps[i - 1]).total_seconds() / 86400
        for i in range(1, len(timestamps))
    ]
    return sum(deltas) / len(deltas)
