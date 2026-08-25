"""Teste de integração da trilha de estudo (simulados).

Prova, contra um banco real, que `GET /simulados/history` (via
`simulado_service.get_history`) aponta a matéria mais fraca a partir do
histórico completo de tentativas concluídas do candidato — não só da
última.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import CandidateProfile
from app.models.simulado import SimuladoAnswer, SimuladoAttempt, SimuladoQuestion
from app.models.user import User
from app.services import simulado_service


async def _seed_finished_attempt(
    db: AsyncSession,
    *,
    candidate_profile_id,
    portugues_correct: int,
    portugues_total: int,
    matematica_correct: int,
    matematica_total: int,
) -> None:
    attempt = SimuladoAttempt(
        candidate_profile_id=candidate_profile_id,
        total_questions=portugues_total + matematica_total,
        correct_count=portugues_correct + matematica_correct,
        finished_at=datetime.now(UTC),
    )
    db.add(attempt)
    await db.flush()

    async def _add_answers(subject: str, correct: int, total: int) -> None:
        for i in range(total):
            question = SimuladoQuestion(
                subject=subject,
                statement=f"Questão {subject} {i} {attempt.id}",
                options=[{"key": "a", "text": "A"}, {"key": "b", "text": "B"}],
                correct_option_key="a",
                explanation="explicação",
            )
            db.add(question)
            await db.flush()
            db.add(
                SimuladoAnswer(
                    attempt_id=attempt.id,
                    question_id=question.id,
                    selected_option_key="a" if i < correct else "b",
                    is_correct=i < correct,
                )
            )
        await db.flush()

    await _add_answers("portugues", portugues_correct, portugues_total)
    await _add_answers("matematica", matematica_correct, matematica_total)


async def test_trilha_de_estudo_aponta_materia_mais_fraca_do_historico(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await db_session.get(User, candidate_profile.user_id)
    assert user is not None

    # Duas tentativas: no total, português vai bem (9/10) e matemática mal (2/10).
    await _seed_finished_attempt(
        db_session,
        candidate_profile_id=candidate_profile.id,
        portugues_correct=5,
        portugues_total=5,
        matematica_correct=1,
        matematica_total=5,
    )
    await _seed_finished_attempt(
        db_session,
        candidate_profile_id=candidate_profile.id,
        portugues_correct=4,
        portugues_total=5,
        matematica_correct=1,
        matematica_total=5,
    )

    history = await simulado_service.get_history(db_session, user)

    assert history.weakest_subject == "matematica"
    assert len(history.attempts) == 2


async def test_sem_tentativa_concluida_weakest_subject_e_none(
    db_session: AsyncSession, candidate_profile: CandidateProfile
) -> None:
    user = await db_session.get(User, candidate_profile.user_id)
    assert user is not None

    history = await simulado_service.get_history(db_session, user)

    assert history.weakest_subject is None
    assert history.attempts == []
