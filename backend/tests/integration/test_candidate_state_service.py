"""Teste de integração de `app.services.candidate_state_service` (fase N1).

Prova, contra um banco real, que o serviço monta o payload sem quebrar para
um candidato mínimo (sem missões, sem documentos, sem coorte, sem
responsável) — o cenário mais comum logo após o cadastro, e o mais fácil de
esquecer ao escrever um agregado que depende de várias tabelas opcionais.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.candidate_state_scoring import MOMENTUM_FLUID, STATE_VERSION
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.services import candidate_state_service


async def test_candidato_recem_cadastrado_e_fluid(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await db_session.get(User, candidate_profile.user_id)
    assert user is not None

    state = await candidate_state_service.get_candidate_state(db_session, user)

    assert state.version == STATE_VERSION
    # Perfil recém-criado: `created_at` é "agora" na prática, então
    # `days_since_last_activity` fica perto de 0 e sem nenhum sinal de
    # fricção — o caso saudável por definição.
    assert state.momentum == MOMENTUM_FLUID
    assert state.current_step_key == "inscricao"
    # Catálogo de documentos obrigatórios (3 tipos) não recebeu nenhum envio.
    assert state.pending_required_documents == 3
    assert state.days_to_exam is None
    assert state.guardian_training_overdue is False
