"""Teste de integração de `candidate_state_service.track_client_event` (N2/N3/N4).

Endpoint compartilhado por Next Best Action (`nba_clicked`), Zero-Click
Recovery (`step_resumed`) e Modo Resgate (`recovery_*`) — um teste por
fluxo aqui garante que os três continuam gravando corretamente sem
precisar de três serviços quase idênticos.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_event import ActivityEvent
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.services import candidate_state_service


async def test_evento_client_side_e_persistido_com_props(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await db_session.get(User, candidate_profile.user_id)
    assert user is not None

    await candidate_state_service.track_client_event(
        db_session,
        user,
        name="recovery_entered",
        props={"trigger": "dashboard_banner"},
    )

    rows = (
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
    assert len(rows) == 1
    assert rows[0].name == "recovery_entered"
    assert rows[0].props == {"trigger": "dashboard_banner"}
