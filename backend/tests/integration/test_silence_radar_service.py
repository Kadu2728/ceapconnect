"""Teste de integração do Radar de Silêncio ("Jornada que Respira" — metade B).

O freio central da feature tem teste próprio: **quem declarou pausa nunca
gera sinal de silêncio**. Sinalizar quem avisou faria o produto punir a
honestidade — o oposto exato do que a metade A construiu.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.candidate_state_scoring import STALLED_INACTIVITY_DAYS
from app.core.risk_scoring import CandidateRiskFeatures
from app.models.activity_event import ActivityEvent
from app.models.candidate_profile import CandidateProfile
from app.models.silence_signal import SilenceSignal
from app.repositories.silence_signal_repository import SilenceSignalRepository
from app.repositories.user_repository import UserRepository
from app.schemas.journey_pause import PauseStartRequest
from app.services import journey_pause_service, silence_radar_service


def _features(profile_id: uuid.UUID, *, days_silent: float) -> CandidateRiskFeatures:
    """Features mínimas — só o campo que o Radar consulta importa aqui."""
    return CandidateRiskFeatures(
        candidate_profile_id=str(profile_id),
        days_since_last_activity=days_silent,
        mission_completion_ratio=0.0,
        missions_abandoned_count=0,
        avg_days_between_completions=None,
        is_stuck_on_blocking_step=False,
        current_step_key="documentacao",
        current_step_label="Documentação",
        below_cohort_median=None,
        cohort_median_completion_ratio=None,
        guardian_has_contact=False,
        guardian_training_attended=False,
        guardian_training_overdue=False,
    )


async def _open_signal(db: AsyncSession, profile_id: uuid.UUID) -> SilenceSignal | None:
    return (await SilenceSignalRepository(db).map_open_by_profile_ids([profile_id])).get(profile_id)


async def test_cruzar_o_limiar_abre_um_sinal(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    opened = await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS + 1)]
    )

    assert opened == 1
    signal = await _open_signal(db_session, candidate_profile.id)
    assert signal is not None
    assert signal.step_key == "documentacao"
    assert signal.returned_at is None


async def test_abaixo_do_limiar_nao_abre_sinal(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    opened = await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS - 1)]
    )

    assert opened == 0
    assert await _open_signal(db_session, candidate_profile.id) is None


async def test_rodar_duas_vezes_nao_duplica_o_sinal(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """O job roda de hora em hora — sem isso, "quem entrou em silêncio esta
    semana" viraria uma contagem de execuções do job, não de pessoas."""
    features = [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS + 2)]

    first = await silence_radar_service.sync_signals(db_session, features)
    second = await silence_radar_service.sync_signals(db_session, features)

    assert first == 1
    assert second == 0


async def test_candidato_que_volta_tem_o_sinal_fechado(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS + 3)]
    )
    assert await _open_signal(db_session, candidate_profile.id) is not None

    await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=0.0)]
    )

    assert await _open_signal(db_session, candidate_profile.id) is None


async def test_pausa_declarada_nunca_gera_sinal_de_silencio(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """O freio central: quem avisou que precisava de uns dias não está em
    silêncio — está exatamente onde disse que estaria."""
    user = await UserRepository(db_session).get_by_id(candidate_profile.user_id)
    assert user is not None
    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=7))

    opened = await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS + 10)]
    )

    assert opened == 0
    assert await _open_signal(db_session, candidate_profile.id) is None


async def test_pausar_depois_de_sumir_fecha_o_sinal_aberto(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """A partir do aviso, a ausência deixou de ser inexplicada."""
    await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS + 1)]
    )
    assert await _open_signal(db_session, candidate_profile.id) is not None

    user = await UserRepository(db_session).get_by_id(candidate_profile.user_id)
    assert user is not None
    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=7))

    await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS + 2)]
    )

    assert await _open_signal(db_session, candidate_profile.id) is None


async def test_radar_nao_escreve_no_log_comportamental(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    """Regressão do erro que quebraria a feature inteira: `days_since_last_activity`
    vem de `MAX(activity_events.occurred_at)` — se o Radar gravasse o silêncio
    ali, o candidato pareceria **ativo** no instante em que foi detectado
    silencioso, e o Radar apagaria o próprio sinal."""
    before = (
        (
            await db_session.execute(
                select(ActivityEvent).where(
                    ActivityEvent.candidate_profile_id == candidate_profile.id
                )
            )
        )
        .scalars()
        .all()
    )

    await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS + 5)]
    )

    after = (
        (
            await db_session.execute(
                select(ActivityEvent).where(
                    ActivityEvent.candidate_profile_id == candidate_profile.id
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(after) == len(before)


async def test_contagem_de_travessias_recentes(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    repo = SilenceSignalRepository(db_session)
    since = datetime.now(UTC) - timedelta(days=7)
    before = await repo.count_detected_since(since=since)

    await silence_radar_service.sync_signals(
        db_session, [_features(candidate_profile.id, days_silent=STALLED_INACTIVITY_DAYS + 1)]
    )

    assert await repo.count_detected_since(since=since) == before + 1
