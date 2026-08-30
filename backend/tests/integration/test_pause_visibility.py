"""Testes de integração das fases C e D da Pausa Declarada.

C — o Console de Intervenção distingue "avisou que precisava de uns dias" de
"sumiu sem avisar", sem nunca expor o motivo da pausa por candidato.
D — a taxa de retorno após pausa sai dos eventos já emitidos.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import CohortScope
from app.models.candidate_profile import CandidateProfile
from app.models.user import ROLE_ADMIN, User
from app.repositories.risk_score_repository import RiskScoreRepository
from app.repositories.user_repository import UserRepository
from app.schemas.journey_pause import PauseStartRequest
from app.schemas.risk import RiskQueueItem
from app.services import journey_os_metrics_service, journey_pause_service, risk_service


async def _admin_scope(db: AsyncSession, user: User) -> CohortScope:
    """Escopo irrestrito (admin) — a fila inteira, sem filtro de coorte."""
    user.role = ROLE_ADMIN
    user.is_admin = True
    await db.flush()
    return CohortScope(user=user, cohort_ids=None)


async def _ensure_scored(db: AsyncSession, profile: CandidateProfile) -> None:
    """Um candidato só entra na fila depois de ter score calculado."""
    await RiskScoreRepository(db).upsert(
        candidate_profile_id=profile.id,
        score=80,
        tier="alto",
        factors=[],
        explanation="Teste de pausa no console.",
        features={},
        model_version="test",
    )
    await db.flush()


async def test_fila_marca_candidato_em_pausa_declarada(
    db_session: AsyncSession, candidate_profile: CandidateProfile, guardian_user: User
) -> None:
    await _ensure_scored(db_session, candidate_profile)
    user = await UserRepository(db_session).get_by_id(candidate_profile.user_id)
    assert user is not None
    await journey_pause_service.start_pause(
        db_session, user, PauseStartRequest(days=3, reason_code="trabalho")
    )

    queue = await risk_service.get_queue(db_session, await _admin_scope(db_session, guardian_user))

    row = next(item for item in queue.items if item.candidate_profile_id == candidate_profile.id)
    assert row.paused_until is not None
    assert row.paused_until > datetime.now(UTC)
    assert queue.paused_count >= 1


async def test_fila_nunca_expoe_o_motivo_da_pausa(
    db_session: AsyncSession, candidate_profile: CandidateProfile, guardian_user: User
) -> None:
    """Freio de privacidade: "pausou por trabalho" ao lado do nome de um menor
    convida julgamento sobre a vida dele. O motivo só existe em agregado."""
    await _ensure_scored(db_session, candidate_profile)
    user = await UserRepository(db_session).get_by_id(candidate_profile.user_id)
    assert user is not None
    await journey_pause_service.start_pause(
        db_session, user, PauseStartRequest(days=3, reason_code="trabalho")
    )

    queue = await risk_service.get_queue(db_session, await _admin_scope(db_session, guardian_user))

    field_names = set(RiskQueueItem.model_fields.keys())
    assert not {f for f in field_names if "reason" in f or "motivo" in f}
    serialized = queue.items[0].model_dump_json()
    assert "trabalho" not in serialized


async def test_candidato_sem_pausa_nao_e_marcado(
    db_session: AsyncSession, candidate_profile: CandidateProfile, guardian_user: User
) -> None:
    await _ensure_scored(db_session, candidate_profile)

    queue = await risk_service.get_queue(db_session, await _admin_scope(db_session, guardian_user))

    row = next(item for item in queue.items if item.candidate_profile_id == candidate_profile.id)
    assert row.paused_until is None


async def test_metricas_contam_pausa_e_taxa_de_retorno(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await UserRepository(db_session).get_by_id(candidate_profile.user_id)
    assert user is not None

    before = await journey_os_metrics_service.get_metrics(db_session, window_days=30)

    await journey_pause_service.start_pause(db_session, user, PauseStartRequest(days=3))
    await journey_pause_service.resume_pause(db_session, user)

    after = await journey_os_metrics_service.get_metrics(db_session, window_days=30)

    assert after.pause_started_count == before.pause_started_count + 1
    assert after.pause_resumed_count == before.pause_resumed_count + 1
    assert after.pause_return_rate is not None


async def test_taxa_de_retorno_e_none_sem_nenhuma_pausa(db_session: AsyncSession) -> None:
    """`None`, nunca `0.0`: "ninguém pausou" é diferente de "pausaram e não
    voltaram" — mesma disciplina de `safe_rate` nas outras taxas."""
    metrics = await journey_os_metrics_service.get_metrics(db_session, window_days=0)

    assert metrics.pause_started_count == 0
    assert metrics.pause_return_rate is None
