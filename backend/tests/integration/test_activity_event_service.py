"""Teste de integração de `app.services.activity_event_service` (fase F1).

Prova, contra um banco real, que os nomes de evento novos da fase F1
(`step_abandoned`, `nba_generated`, etc.) são de fato aceitos pela
`CHECK CONSTRAINT` de `activity_events.name` depois da migration
`a8b9c0d1e2f3` — o teste unitário (`test_activity_event_vocabulary.py`)
garante que o Python está consistente consigo mesmo, mas só o banco garante
que a constraint em produção bate com o que o Python acredita ser válido.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_event import EVENT_NBA_GENERATED, ActivityEvent
from app.models.candidate_profile import CandidateProfile
from app.services import activity_event_service


async def test_evento_da_fase_f1_e_persistido(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    await activity_event_service.track_committed(
        db_session,
        candidate_profile_id=candidate_profile.id,
        name=EVENT_NBA_GENERATED,
        props={"action_key": "enviar_documento"},
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
    assert rows[0].name == EVENT_NBA_GENERATED
    assert rows[0].props == {"action_key": "enviar_documento"}
