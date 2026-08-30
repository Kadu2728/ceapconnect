"""Regra de negócio do Next Best Action Engine (Candidate Journey OS — fase N2).

Ponte entre o Candidate State (N1) e a camada pura de regras
(`app.core.next_best_action_rules`) — mesmo papel que `risk_service.py` faz
para `risk_scoring.py`. Também é o ponto que registra `nba_generated`: toda
recomendação de fato mostrada ao candidato deixa rastro no log
comportamental, para o Learning Loop (F2) medir CTR e conclusão depois
(`nba_generated → nba_clicked → nba_completed`).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.next_best_action_rules import NextBestAction, NextBestActionInput, recommend
from app.models.activity_event import EVENT_NBA_GENERATED
from app.models.user import User
from app.services import activity_event_service, candidate_state_service
from app.services.candidate_profile_service import get_profile_or_raise


async def get_next_best_action(db: AsyncSession, user: User) -> NextBestAction | None:
    """Recomendação atual do candidato autenticado, ou `None` se nada for acionável."""
    state = await candidate_state_service.get_candidate_state(db, user)

    # Pausa declarada tem precedência: o candidato avisou que a vida apertou,
    # e o produto para de cobrar avanço enquanto isso. Recomendar uma ação
    # agora seria cobrar de quem acabou de pedir um respiro — e nenhum
    # `nba_generated` deve ser contado, já que nada será mostrado.
    if state.pause is not None:
        return None

    action = recommend(
        NextBestActionInput(
            momentum=state.momentum,
            pending_required_documents=state.pending_required_documents,
            guardian_training_overdue=state.guardian_training_overdue,
            days_to_exam=state.days_to_exam,
        )
    )

    if action is not None:
        profile = await get_profile_or_raise(db, user)
        await activity_event_service.track_committed(
            db,
            candidate_profile_id=profile.id,
            name=EVENT_NBA_GENERATED,
            props={"action_key": action.action_key},
        )

    return action
