"""Teste de integração de `app.services.next_best_action_service` (fase N2).

Prova, contra um banco real, que a recomendação de um candidato recém-
cadastrado (3 documentos obrigatórios pendentes) é "enviar documentos" e
que a geração da recomendação deixa rastro em `activity_events`
(`nba_generated`) — a base do Learning Loop (F2).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.next_best_action_rules import ACTION_UPLOAD_DOCUMENTS
from app.models.activity_event import EVENT_NBA_GENERATED, ActivityEvent
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.services import next_best_action_service


async def test_candidato_recem_cadastrado_recebe_recomendacao_de_documentos(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await db_session.get(User, candidate_profile.user_id)
    assert user is not None

    action = await next_best_action_service.get_next_best_action(db_session, user)

    assert action is not None
    assert action.action_key == ACTION_UPLOAD_DOCUMENTS

    rows = (
        (
            await db_session.execute(
                select(ActivityEvent).where(
                    ActivityEvent.candidate_profile_id == candidate_profile.id,
                    ActivityEvent.name == EVENT_NBA_GENERATED,
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(rows) == 1
    assert rows[0].props == {"action_key": ACTION_UPLOAD_DOCUMENTS}
