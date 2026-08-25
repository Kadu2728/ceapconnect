"""Acesso a dados dos Simulados de prova (EPIC 16).

Isola toda query relacionada a questões, tentativas e respostas — a camada de
services nunca deve montar SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simulado import (
    SimuladoAnswer,
    SimuladoAttempt,
    SimuladoQuestion,
    SimuladoSubject,
)


class SimuladoQuestionRepository:
    """Repositório de leitura do banco de questões."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_random_by_subject(
        self, subject: SimuladoSubject, *, limit: int
    ) -> list[SimuladoQuestion]:
        """Sorteia até `limit` questões de uma matéria (`ORDER BY random()`).

        Postgres-specific de propósito — o projeto roda só sobre Neon/Postgres,
        e `random()` é a forma mais simples de variar o simulado a cada
        tentativa sem manter estado de "quais já caíram".
        """
        stmt = (
            select(SimuladoQuestion)
            .where(SimuladoQuestion.subject == subject)
            .order_by(func.random())
            .limit(limit)
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def get_by_id(self, question_id: uuid.UUID) -> SimuladoQuestion | None:
        """Busca uma questão pelo id (usada ao corrigir uma resposta)."""
        return await self._db.get(SimuladoQuestion, question_id)

    async def get_by_statement(self, statement: str) -> SimuladoQuestion | None:
        """Busca pela chave natural do seed (evita duplicar em reexecuções)."""
        stmt = select(SimuladoQuestion).where(SimuladoQuestion.statement == statement)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def count_all(self) -> int:
        stmt = select(func.count()).select_from(SimuladoQuestion)
        return int((await self._db.execute(stmt)).scalar_one())


class SimuladoAttemptRepository:
    """Repositório de leitura/escrita das tentativas de simulado."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self, *, candidate_profile_id: uuid.UUID, total_questions: int
    ) -> SimuladoAttempt:
        """Inicia uma nova tentativa (flush, sem commit)."""
        attempt = SimuladoAttempt(
            candidate_profile_id=candidate_profile_id, total_questions=total_questions
        )
        self._db.add(attempt)
        await self._db.flush()
        return attempt

    async def get_for_profile(
        self, *, attempt_id: uuid.UUID, candidate_profile_id: uuid.UUID
    ) -> SimuladoAttempt | None:
        """Busca uma tentativa garantindo que pertence ao candidato (posse)."""
        stmt = select(SimuladoAttempt).where(
            SimuladoAttempt.id == attempt_id,
            SimuladoAttempt.candidate_profile_id == candidate_profile_id,
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def list_finished_for_profile(
        self, candidate_profile_id: uuid.UUID
    ) -> list[SimuladoAttempt]:
        """Histórico de tentativas concluídas, mais recentes primeiro."""
        stmt = (
            select(SimuladoAttempt)
            .where(
                SimuladoAttempt.candidate_profile_id == candidate_profile_id,
                SimuladoAttempt.finished_at.is_not(None),
            )
            .order_by(SimuladoAttempt.finished_at.desc())
        )
        return list((await self._db.execute(stmt)).scalars().all())


class SimuladoAnswerRepository:
    """Repositório de leitura/escrita das respostas dentro de uma tentativa."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get(self, *, attempt_id: uuid.UUID, question_id: uuid.UUID) -> SimuladoAnswer | None:
        stmt = select(SimuladoAnswer).where(
            SimuladoAnswer.attempt_id == attempt_id,
            SimuladoAnswer.question_id == question_id,
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def upsert(
        self,
        *,
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
        selected_option_key: str,
        is_correct: bool,
    ) -> SimuladoAnswer:
        """Registra (ou corrige) a resposta a uma questão. Flush, sem commit.

        Permite reenviar: se a página recarregar no meio do simulado, marcar a
        mesma questão de novo apenas atualiza a resposta, em vez de falhar.
        """
        existing = await self.get(attempt_id=attempt_id, question_id=question_id)
        if existing is None:
            existing = SimuladoAnswer(attempt_id=attempt_id, question_id=question_id)
            self._db.add(existing)

        existing.selected_option_key = selected_option_key
        existing.is_correct = is_correct
        await self._db.flush()
        return existing

    async def count_correct_for_attempt(self, attempt_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(SimuladoAnswer)
            .where(SimuladoAnswer.attempt_id == attempt_id, SimuladoAnswer.is_correct.is_(True))
        )
        return int((await self._db.execute(stmt)).scalar_one())

    async def subject_breakdown_for_attempt(
        self, attempt_id: uuid.UUID
    ) -> list[tuple[SimuladoSubject, int, int]]:
        """Acertos × total respondidas, por matéria, dentro de uma tentativa."""
        correct = func.count().filter(SimuladoAnswer.is_correct.is_(True))
        total = func.count()
        stmt = (
            select(SimuladoQuestion.subject, correct, total)
            .join(SimuladoQuestion, SimuladoQuestion.id == SimuladoAnswer.question_id)
            .where(SimuladoAnswer.attempt_id == attempt_id)
            .group_by(SimuladoQuestion.subject)
        )
        rows = (await self._db.execute(stmt)).all()
        return [(row[0], int(row[1]), int(row[2])) for row in rows]

    async def subject_breakdown_for_profile(
        self, candidate_profile_id: uuid.UUID
    ) -> list[tuple[SimuladoSubject, int, int]]:
        """Acertos × total respondidas, por matéria, em todas as tentativas
        **concluídas** do candidato — base da trilha de estudo (aponta a
        matéria mais fraca no histórico inteiro, não só na última tentativa).
        Tentativas não finalizadas ficam de fora (o candidato "recomeça" uma
        tentativa abandonada, ver docstring de `SimuladoAttempt` — não faz
        sentido pesar respostas de uma tentativa que ele nunca fechou).
        """
        correct = func.count().filter(SimuladoAnswer.is_correct.is_(True))
        total = func.count()
        stmt = (
            select(SimuladoQuestion.subject, correct, total)
            .join(SimuladoQuestion, SimuladoQuestion.id == SimuladoAnswer.question_id)
            .join(SimuladoAttempt, SimuladoAttempt.id == SimuladoAnswer.attempt_id)
            .where(
                SimuladoAttempt.candidate_profile_id == candidate_profile_id,
                SimuladoAttempt.finished_at.is_not(None),
            )
            .group_by(SimuladoQuestion.subject)
        )
        rows = (await self._db.execute(stmt)).all()
        return [(row[0], int(row[1]), int(row[2])) for row in rows]
