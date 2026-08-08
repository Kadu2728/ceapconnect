"""Regra de negócio dos Simulados de prova (EPIC 16).

Prepara o candidato para o formato real da prova (Português + Matemática,
questões objetivas) com feedback imediato e pessoal — nunca uma nota
comparada com ninguém, diferente do risk score (que o candidato nunca vê).

Concluir um simulado concede XP (reaproveita o mesmo `xp_total` da
gamificação e `achievement_service.evaluate_mission_achievements`, que já é
agnóstico à origem do XP) — estudar para a prova também deve alimentar a
mesma progressão de nível que o resto do app.
"""

import uuid
from datetime import UTC, datetime
from typing import Final

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.simulado import SUBJECT_MATEMATICA, SUBJECT_PORTUGUES
from app.models.user import User
from app.repositories.mission_repository import MissionProgressRepository
from app.repositories.simulado_repository import (
    SimuladoAnswerRepository,
    SimuladoAttemptRepository,
    SimuladoQuestionRepository,
)
from app.schemas.simulado import (
    AnswerRequest,
    AnswerResult,
    AttemptHistoryItem,
    AttemptHistoryResponse,
    FinishAttemptResponse,
    QuestionOption,
    SimuladoQuestionPublic,
    StartAttemptResponse,
    SubjectBreakdown,
)
from app.services import achievement_service
from app.services.candidate_profile_service import get_profile_or_raise

_QUESTIONS_PER_SUBJECT: Final = 10  # 10 + 10 = 20, o formato real da prova.
_XP_REWARD: Final = 15


async def start_attempt(db: AsyncSession, user: User) -> StartAttemptResponse:
    """Sorteia as questões (10 Português + 10 Matemática) e abre a tentativa."""
    profile = await get_profile_or_raise(db, user)
    question_repo = SimuladoQuestionRepository(db)

    portugues = await question_repo.list_random_by_subject(
        SUBJECT_PORTUGUES, limit=_QUESTIONS_PER_SUBJECT
    )
    matematica = await question_repo.list_random_by_subject(
        SUBJECT_MATEMATICA, limit=_QUESTIONS_PER_SUBJECT
    )
    questions = portugues + matematica
    if not questions:
        raise BadRequestException(
            "Banco de questões vazio. Rode o seed (`python -m app.core.seed`) antes."
        )

    attempt = await SimuladoAttemptRepository(db).create(
        candidate_profile_id=profile.id, total_questions=len(questions)
    )
    await db.commit()

    return StartAttemptResponse(
        attempt_id=attempt.id,
        questions=[
            SimuladoQuestionPublic(
                id=question.id,
                subject=question.subject,
                statement=question.statement,
                options=[QuestionOption(**option) for option in question.options],
            )
            for question in questions
        ],
    )


async def answer_question(
    db: AsyncSession, user: User, attempt_id: uuid.UUID, payload: AnswerRequest
) -> AnswerResult:
    """Registra a resposta a uma questão e devolve feedback imediato."""
    profile = await get_profile_or_raise(db, user)
    attempt = await SimuladoAttemptRepository(db).get_for_profile(
        attempt_id=attempt_id, candidate_profile_id=profile.id
    )
    if attempt is None:
        raise NotFoundException("Tentativa de simulado não encontrada.")
    if attempt.finished_at is not None:
        raise ConflictException("Esta tentativa já foi finalizada.")

    question = await SimuladoQuestionRepository(db).get_by_id(payload.question_id)
    if question is None:
        raise NotFoundException("Questão não encontrada.")

    is_correct = payload.selected_option_key == question.correct_option_key
    await SimuladoAnswerRepository(db).upsert(
        attempt_id=attempt.id,
        question_id=question.id,
        selected_option_key=payload.selected_option_key,
        is_correct=is_correct,
    )
    await db.commit()

    return AnswerResult(
        question_id=question.id,
        is_correct=is_correct,
        correct_option_key=question.correct_option_key,
        explanation=question.explanation,
    )


async def finish_attempt(
    db: AsyncSession, user: User, attempt_id: uuid.UUID
) -> FinishAttemptResponse:
    """Fecha a tentativa, apura o resultado e concede o XP do simulado."""
    profile = await get_profile_or_raise(db, user)
    attempt = await SimuladoAttemptRepository(db).get_for_profile(
        attempt_id=attempt_id, candidate_profile_id=profile.id
    )
    if attempt is None:
        raise NotFoundException("Tentativa de simulado não encontrada.")
    if attempt.finished_at is not None:
        raise ConflictException("Esta tentativa já foi finalizada.")

    answer_repo = SimuladoAnswerRepository(db)
    correct_count = await answer_repo.count_correct_for_attempt(attempt.id)
    breakdown_rows = await answer_repo.subject_breakdown_for_attempt(attempt.id)

    attempt.correct_count = correct_count
    attempt.finished_at = datetime.now(UTC)
    profile.xp_total += _XP_REWARD
    await db.flush()

    completed_missions = await MissionProgressRepository(db).count_completed_for_profile(profile.id)
    await achievement_service.evaluate_mission_achievements(
        db, profile, completed_missions=completed_missions, xp_total=profile.xp_total
    )

    await db.commit()

    score_percentage = (
        round((correct_count / attempt.total_questions) * 100) if attempt.total_questions else 0
    )
    return FinishAttemptResponse(
        attempt_id=attempt.id,
        correct_count=correct_count,
        total_questions=attempt.total_questions,
        score_percentage=score_percentage,
        subject_breakdown=[
            SubjectBreakdown(subject=subject, correct=correct, total=total)
            for subject, correct, total in breakdown_rows
        ],
        xp_awarded=_XP_REWARD,
    )


async def get_history(db: AsyncSession, user: User) -> AttemptHistoryResponse:
    """Histórico pessoal de simulados — nunca comparado com o de outro candidato."""
    profile = await get_profile_or_raise(db, user)
    attempts = await SimuladoAttemptRepository(db).list_finished_for_profile(profile.id)

    items = [
        AttemptHistoryItem(
            attempt_id=attempt.id,
            finished_at=attempt.finished_at,
            correct_count=attempt.correct_count or 0,
            total_questions=attempt.total_questions,
            score_percentage=(
                round(((attempt.correct_count or 0) / attempt.total_questions) * 100)
                if attempt.total_questions
                else 0
            ),
        )
        for attempt in attempts
        if attempt.finished_at is not None
    ]

    best = max((item.score_percentage for item in items), default=None)
    return AttemptHistoryResponse(attempts=items, best_score_percentage=best)
