"""Regra de negócio do módulo de Videoaulas.

Compõe catálogo + progresso individual nas respostas que a UI consome, e é
o **único** lugar onde a autorização por público acontece — nunca no front.

Regra de acesso (`_assert_can_view`): admin e coordenador enxergam qualquer
curso (gestão); candidato e responsável só enxergam o público igual ao
próprio papel. Trocar o slug na URL para um curso de outro público devolve
403 antes de qualquer dado do curso ser lido.

Progresso: `position_seconds` nunca regride (um scrub para trás não apaga o
que já foi assistido), e a aula conclui sozinha ao cruzar
`COMPLETION_THRESHOLD`. `completed_at`, uma vez gravado, é permanente —
reassistir não "desconclui".
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.rbac import is_admin
from app.models.learning import COMPLETION_THRESHOLD, Course, Lesson, LessonProgress
from app.models.user import ROLE_COORDINATOR, User
from app.repositories.learning_repository import LearningRepository
from app.schemas.learning import (
    CourseCard,
    CourseOverview,
    LessonDetail,
    LessonStatus,
    LessonSummary,
    ModuleSummary,
    ProgressUpdateResult,
)

_COURSE_NOT_FOUND = "Curso não encontrado."
_LESSON_NOT_FOUND = "Aula não encontrada."
_FORBIDDEN = "Este conteúdo não é destinado ao seu perfil."


async def list_courses(db: AsyncSession, user: User) -> list[CourseCard]:
    """Cursos que esta pessoa pode ver — filtrados por público na query."""
    audience = None if _is_staff(user) else user.role
    courses = await LearningRepository(db).list_active_courses(audience=audience)  # type: ignore[arg-type]
    return [CourseCard.model_validate(course, from_attributes=True) for course in courses]


async def get_course_overview(db: AsyncSession, user: User, slug: str) -> CourseOverview:
    """A página inteira da formação: módulos, aulas com estado, progresso e próxima aula."""
    repo = LearningRepository(db)
    course = await repo.get_course_by_slug(slug)
    if course is None or (not course.is_active and not _is_staff(user)):
        raise NotFoundException(_COURSE_NOT_FOUND)
    _assert_can_view(user, course)

    modules = await repo.list_modules(course.id)
    lessons = await repo.list_active_lessons_for_modules([m.id for m in modules])
    progress_map = await repo.map_progress_for_lessons(
        user_id=user.id, lesson_ids=[lesson.id for lesson in lessons]
    )

    lessons_by_module: dict[uuid.UUID, list[Lesson]] = {}
    for lesson in lessons:
        lessons_by_module.setdefault(lesson.module_id, []).append(lesson)

    module_summaries: list[ModuleSummary] = []
    all_summaries: list[LessonSummary] = []
    for module in modules:
        summaries = [
            _to_lesson_summary(lesson, progress_map.get(lesson.id))
            for lesson in lessons_by_module.get(module.id, [])
        ]
        all_summaries.extend(summaries)
        module_summaries.append(
            ModuleSummary(
                id=module.id,
                title=module.title,
                description=module.description,
                order=module.order,
                lessons=summaries,
                completed_count=sum(1 for s in summaries if s.status == "completed"),
            )
        )

    completed = sum(1 for s in all_summaries if s.status == "completed")
    total = len(all_summaries)

    return CourseOverview(
        course=CourseCard.model_validate(course, from_attributes=True),
        modules=module_summaries,
        total_lessons=total,
        completed_lessons=completed,
        progress_percent=round(completed / total * 100) if total else 0,
        # "Próxima" = a primeira ainda não concluída na ordem do curso. Uma
        # aula em andamento tem prioridade natural por vir antes na sequência.
        next_lesson=next((s for s in all_summaries if s.status != "completed"), None),
    )


async def get_lesson(db: AsyncSession, user: User, lesson_id: uuid.UUID) -> LessonDetail:
    """A aula para assistir — única resposta que carrega o vídeo.

    A autorização acontece **antes** de montar qualquer campo: uma aula de
    curso de outro público devolve 403 sem revelar nem o título.
    """
    repo = LearningRepository(db)
    pair = await repo.get_lesson_with_course(lesson_id)
    if pair is None:
        raise NotFoundException(_LESSON_NOT_FOUND)
    lesson, course = pair
    if not lesson.is_active and not _is_staff(user):
        raise NotFoundException(_LESSON_NOT_FOUND)
    _assert_can_view(user, course)

    # Vizinhas para o "próxima aula" dentro do player — na ordem do curso
    # inteiro, não só do módulo (a última aula de um módulo aponta para a
    # primeira do seguinte).
    modules = await repo.list_modules(course.id)
    ordered = await repo.list_active_lessons_for_modules([m.id for m in modules])
    module_order = {m.id: m.order for m in modules}
    ordered.sort(key=lambda item: (module_order[item.module_id], item.order))
    ids = [item.id for item in ordered]
    index = ids.index(lesson.id)

    progress = await repo.get_progress(user_id=user.id, lesson_id=lesson.id)
    module_title = next(m.title for m in modules if m.id == lesson.module_id)

    return LessonDetail(
        id=lesson.id,
        course_slug=course.slug,
        course_title=course.title,
        module_title=module_title,
        title=lesson.title,
        description=lesson.description,
        video_provider=lesson.video_provider,
        video_ref=lesson.video_ref,
        duration_seconds=lesson.duration_seconds,
        status=_status_of(lesson, progress),
        resume_position_seconds=_resume_position(lesson, progress),
        previous_lesson_id=ids[index - 1] if index > 0 else None,
        next_lesson_id=ids[index + 1] if index + 1 < len(ids) else None,
    )


async def update_progress(
    db: AsyncSession, user: User, lesson_id: uuid.UUID, position_seconds: int
) -> ProgressUpdateResult:
    """Grava a posição assistida e conclui a aula ao cruzar o limiar.

    Idempotente e monotônica: a posição guardada é sempre o **máximo** já
    visto (voltar 30s para rever um trecho não apaga progresso), e uma aula
    concluída nunca volta a "em andamento".
    """
    repo = LearningRepository(db)
    pair = await repo.get_lesson_with_course(lesson_id)
    if pair is None:
        raise NotFoundException(_LESSON_NOT_FOUND)
    lesson, course = pair
    _assert_can_view(user, course)

    now = datetime.now(UTC)
    progress = await repo.get_progress(user_id=user.id, lesson_id=lesson.id)
    if progress is None:
        progress = await repo.create_progress(user_id=user.id, lesson_id=lesson.id, started_at=now)

    # Clampa no tamanho do vídeo: um `timeupdate` no último frame pode passar
    # de `duration` por arredondamento, e isso não pode virar >100%.
    clamped = min(position_seconds, lesson.duration_seconds)
    progress.position_seconds = max(progress.position_seconds, clamped)

    just_completed = False
    crossed_threshold = _watched_fraction(lesson, progress) >= COMPLETION_THRESHOLD
    if progress.completed_at is None and crossed_threshold:
        progress.completed_at = now
        just_completed = True

    await db.commit()

    return ProgressUpdateResult(
        lesson_id=lesson.id,
        status=_status_of(lesson, progress),
        watched_percent=_watched_percent(lesson, progress),
        resume_position_seconds=_resume_position(lesson, progress),
        completed_at=progress.completed_at,
        just_completed=just_completed,
    )


# --- helpers ------------------------------------------------------------------


def _is_staff(user: User) -> bool:
    """Admin e coordenador enxergam todo curso — é gestão, não consumo."""
    return is_admin(user) or user.role == ROLE_COORDINATOR


def _assert_can_view(user: User, course: Course) -> None:
    if _is_staff(user):
        return
    if course.audience != user.role:
        raise ForbiddenException(_FORBIDDEN)


def _watched_fraction(lesson: Lesson, progress: LessonProgress | None) -> float:
    if progress is None or lesson.duration_seconds <= 0:
        return 0.0
    return min(1.0, progress.position_seconds / lesson.duration_seconds)


def _watched_percent(lesson: Lesson, progress: LessonProgress | None) -> int:
    return round(_watched_fraction(lesson, progress) * 100)


def _status_of(lesson: Lesson, progress: LessonProgress | None) -> LessonStatus:
    if progress is None:
        return "available"
    if progress.completed_at is not None:
        return "completed"
    return "in_progress" if progress.position_seconds > 0 else "available"


def _resume_position(lesson: Lesson, progress: LessonProgress | None) -> int:
    """De onde retomar. Aula concluída recomeça do zero — reassistir é uma
    escolha, não uma continuação."""
    if progress is None or progress.completed_at is not None:
        return 0
    return progress.position_seconds


def _to_lesson_summary(lesson: Lesson, progress: LessonProgress | None) -> LessonSummary:
    return LessonSummary(
        id=lesson.id,
        title=lesson.title,
        description=lesson.description,
        duration_seconds=lesson.duration_seconds,
        order=lesson.order,
        status=_status_of(lesson, progress),
        watched_percent=_watched_percent(lesson, progress),
        resume_position_seconds=_resume_position(lesson, progress),
    )
