"""Teste de integração de `app.services.journey_os_metrics_service` (fase F2).

Prova, contra um banco real, que as contagens globais batem com os eventos
gravados e que as taxas são calculadas corretamente — a ponta final do
Learning Loop (Signal → Decision → Action → medido aqui).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_event import (
    EVENT_NBA_CLICKED,
    EVENT_NBA_GENERATED,
    EVENT_RECOVERY_ENTERED,
    EVENT_STEP_RESUMED,
)
from app.models.candidate_profile import CandidateProfile
from app.services import activity_event_service, journey_os_metrics_service


async def test_ctr_e_taxa_de_retomada_sao_calculadas_a_partir_dos_eventos(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    # 2 NBAs gerados, 1 clicado -> CTR 0.5.
    await activity_event_service.track_committed(
        db_session, candidate_profile_id=candidate_profile.id, name=EVENT_NBA_GENERATED
    )
    await activity_event_service.track_committed(
        db_session, candidate_profile_id=candidate_profile.id, name=EVENT_NBA_GENERATED
    )
    await activity_event_service.track_committed(
        db_session, candidate_profile_id=candidate_profile.id, name=EVENT_NBA_CLICKED
    )
    # 1 entrada no Modo Resgate, sem retomada ainda -> taxa 0.0 (não None:
    # já existe denominador, só ninguém clicou "Continuar" ainda).
    await activity_event_service.track_committed(
        db_session, candidate_profile_id=candidate_profile.id, name=EVENT_RECOVERY_ENTERED
    )

    metrics = await journey_os_metrics_service.get_metrics(db_session, window_days=30)

    assert metrics.nba_generated_count == 2
    assert metrics.nba_clicked_count == 1
    assert metrics.nba_click_through_rate == 0.5
    assert metrics.recovery_entered_count == 1
    assert metrics.recovery_resumed_count == 0
    assert metrics.recovery_resume_rate == 0.0


async def test_sem_nenhum_evento_as_taxas_sao_none(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    metrics = await journey_os_metrics_service.get_metrics(db_session, window_days=30)

    assert metrics.nba_generated_count == 0
    assert metrics.nba_click_through_rate is None
    assert metrics.recovery_entered_count == 0
    assert metrics.recovery_resume_rate is None


async def test_evento_de_outro_tipo_nao_conta_para_step_resumed(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    await activity_event_service.track_committed(
        db_session, candidate_profile_id=candidate_profile.id, name=EVENT_RECOVERY_ENTERED
    )
    await activity_event_service.track_committed(
        db_session, candidate_profile_id=candidate_profile.id, name=EVENT_STEP_RESUMED
    )

    metrics = await journey_os_metrics_service.get_metrics(db_session, window_days=30)

    assert metrics.recovery_entered_count == 1
    assert metrics.recovery_resumed_count == 1
    assert metrics.recovery_resume_rate == 1.0
