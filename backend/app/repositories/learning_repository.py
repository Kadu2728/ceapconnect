"""Acesso a dados do módulo de Videoaulas (catálogo + progresso).

Isola todas as queries de `Course`/`CourseModule`/`Lesson`/`LessonProgress`
— a camada de services nunca monta SQL/ORM diretamente.

Desenhado para a página "Formação de Pais" carregar leve: o curso inteiro
(módulos + aulas + progresso da pessoa) sai em **três queries fixas**, nunca
uma por módulo ou por aula. Numa conexão 3G instável, cada round-trip a
mais é um segundo de tela em branco.
"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning import Course, CourseAudience, CourseModule, Lesson, LessonProgress


class LearningRepository:
    """Repositório de leitura/escrita do catálogo de cursos e do progresso."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # --- Catálogo -----------------------------------------------------------

    async def list_active_courses(self, *, audience: CourseAudience | None) -> list[Course]:
        """Cursos ativos, opcionalmente filtrados por público.

        `audience=None` = todos (gestão). O filtro acontece **na query**, não
        em memória: um responsável não deve sequer conseguir enumerar cursos
        de outro público.
        """
        stmt = select(Course).where(Course.is_active.is_(True))
        if audience is not None:
            stmt = stmt.where(Course.audience == audience)
        return list((await self._db.execute(stmt.order_by(Course.title))).scalars().all())

    async def get_course_by_slug(self, slug: str) -> Course | None:
        stmt = select(Course).where(Course.slug == slug)
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def get_course_by_id(self, course_id: uuid.UUID) -> Course | None:
        return await self._db.get(Course, course_id)

    async def list_modules(self, course_id: uuid.UUID) -> list[CourseModule]:
        stmt = (
            select(CourseModule)
            .where(CourseModule.course_id == course_id)
            .order_by(CourseModule.order)
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def list_active_lessons_for_modules(self, module_ids: list[uuid.UUID]) -> list[Lesson]:
        """Todas as aulas ativas de vários módulos numa query só (evita N+1)."""
        if not module_ids:
            return []
        stmt = (
            select(Lesson)
            .where(Lesson.module_id.in_(module_ids), Lesson.is_active.is_(True))
            .order_by(Lesson.module_id, Lesson.order)
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def get_lesson_with_course(self, lesson_id: uuid.UUID) -> tuple[Lesson, Course] | None:
        """Aula + o curso dono dela, numa query — é o que a autorização por
        público precisa antes de liberar qualquer dado da aula."""
        stmt = (
            select(Lesson, Course)
            .join(CourseModule, CourseModule.id == Lesson.module_id)
            .join(Course, Course.id == CourseModule.course_id)
            .where(Lesson.id == lesson_id)
        )
        row = (await self._db.execute(stmt)).first()
        return (row[0], row[1]) if row is not None else None

    # --- Gestão (admin) -----------------------------------------------------

    async def list_all_courses(self) -> list[Course]:
        """Todos os cursos, ativos e inativos — só para o painel de gestão."""
        stmt = select(Course).order_by(Course.audience, Course.title)
        return list((await self._db.execute(stmt)).scalars().all())

    async def count_modules_and_lessons(
        self, course_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, tuple[int, int]]:
        """(módulos, aulas) por curso, em duas queries agregadas — nunca N+1."""
        if not course_ids:
            return {}
        module_counts = (
            await self._db.execute(
                select(CourseModule.course_id, func.count())
                .where(CourseModule.course_id.in_(course_ids))
                .group_by(CourseModule.course_id)
            )
        ).all()
        lesson_counts = (
            await self._db.execute(
                select(CourseModule.course_id, func.count())
                .join(Lesson, Lesson.module_id == CourseModule.id)
                .where(CourseModule.course_id.in_(course_ids))
                .group_by(CourseModule.course_id)
            )
        ).all()
        modules_by = {course_id: count for course_id, count in module_counts}
        lessons_by = {course_id: count for course_id, count in lesson_counts}
        return {cid: (modules_by.get(cid, 0), lessons_by.get(cid, 0)) for cid in course_ids}

    async def list_lessons_for_modules(self, module_ids: list[uuid.UUID]) -> list[Lesson]:
        """Todas as aulas (inclusive inativas) — a gestão precisa vê-las para reativar."""
        if not module_ids:
            return []
        stmt = (
            select(Lesson)
            .where(Lesson.module_id.in_(module_ids))
            .order_by(Lesson.module_id, Lesson.order)
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def get_module(self, module_id: uuid.UUID) -> CourseModule | None:
        return await self._db.get(CourseModule, module_id)

    async def get_lesson(self, lesson_id: uuid.UUID) -> Lesson | None:
        return await self._db.get(Lesson, lesson_id)

    def add(self, entity: Course | CourseModule | Lesson) -> None:
        """Adiciona à sessão (flush/commit ficam com o service)."""
        self._db.add(entity)

    # --- Progresso ----------------------------------------------------------

    async def map_progress_for_lessons(
        self, *, user_id: uuid.UUID, lesson_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, LessonProgress]:
        """Progresso da pessoa em várias aulas de uma vez (evita N+1)."""
        if not lesson_ids:
            return {}
        stmt = select(LessonProgress).where(
            LessonProgress.user_id == user_id, LessonProgress.lesson_id.in_(lesson_ids)
        )
        rows = (await self._db.execute(stmt)).scalars().all()
        return {progress.lesson_id: progress for progress in rows}

    async def get_progress(
        self, *, user_id: uuid.UUID, lesson_id: uuid.UUID
    ) -> LessonProgress | None:
        stmt = select(LessonProgress).where(
            LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def create_progress(
        self, *, user_id: uuid.UUID, lesson_id: uuid.UUID, started_at: datetime
    ) -> LessonProgress:
        """Abre o progresso (flush, sem commit — quem chama controla a transação)."""
        progress = LessonProgress(user_id=user_id, lesson_id=lesson_id, started_at=started_at)
        self._db.add(progress)
        await self._db.flush()
        return progress
