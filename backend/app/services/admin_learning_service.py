"""Regra de negócio da gestão de cursos no painel admin.

Cria e edita curso → módulo → aula. Sem exclusão física de propósito:
uma aula pode ter `LessonProgress` de dezenas de pessoas, e apagá-la
apagaria o histórico delas. `is_active=False` esconde do público sem perder
nada — mesmo desenho de `Reward.is_active`.

Reordenar é editar `order`. Sem drag-and-drop na v1: exigiria uma biblioteca
que o painel não tem, para um curso com meia dúzia de aulas.
"""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.learning import (
    VALID_AUDIENCES,
    VALID_PROVIDERS,
    Course,
    CourseModule,
    Lesson,
)
from app.repositories.learning_repository import LearningRepository
from app.schemas.admin_learning import (
    AdminCourseDetail,
    AdminCourseItem,
    AdminCourseListResponse,
    AdminCourseWrite,
    AdminLessonItem,
    AdminLessonWrite,
    AdminModuleItem,
    AdminModuleWrite,
)

_COURSE_NOT_FOUND = "Curso não encontrado."
_MODULE_NOT_FOUND = "Módulo não encontrado."
_LESSON_NOT_FOUND = "Aula não encontrada."
_SLUG_TAKEN = "Já existe um curso com este slug."
_ORDER_TAKEN = "Já existe um item com esta ordem — escolha outro número."


async def list_courses(db: AsyncSession) -> AdminCourseListResponse:
    repo = LearningRepository(db)
    courses = await repo.list_all_courses()
    counts = await repo.count_modules_and_lessons([c.id for c in courses])
    return AdminCourseListResponse(
        courses=[_to_course_item(c, counts.get(c.id, (0, 0))) for c in courses],
        audiences=list(VALID_AUDIENCES),
        providers=list(VALID_PROVIDERS),
    )


async def get_course_detail(db: AsyncSession, course_id: uuid.UUID) -> AdminCourseDetail:
    repo = LearningRepository(db)
    course = await repo.get_course_by_id(course_id)
    if course is None:
        raise NotFoundException(_COURSE_NOT_FOUND)
    return await _build_detail(repo, course)


async def create_course(db: AsyncSession, payload: AdminCourseWrite) -> AdminCourseItem:
    repo = LearningRepository(db)
    if await repo.get_course_by_slug(payload.slug) is not None:
        raise ConflictException(_SLUG_TAKEN)
    course = Course(**payload.model_dump())
    repo.add(course)
    await _commit_or_conflict(db, _SLUG_TAKEN)
    await db.refresh(course)
    return _to_course_item(course, (0, 0))


async def update_course(
    db: AsyncSession, course_id: uuid.UUID, payload: AdminCourseWrite
) -> AdminCourseItem:
    repo = LearningRepository(db)
    course = await repo.get_course_by_id(course_id)
    if course is None:
        raise NotFoundException(_COURSE_NOT_FOUND)
    existing = await repo.get_course_by_slug(payload.slug)
    if existing is not None and existing.id != course.id:
        raise ConflictException(_SLUG_TAKEN)

    for field, value in payload.model_dump().items():
        setattr(course, field, value)
    await _commit_or_conflict(db, _SLUG_TAKEN)
    await db.refresh(course)
    counts = await repo.count_modules_and_lessons([course.id])
    return _to_course_item(course, counts.get(course.id, (0, 0)))


async def create_module(
    db: AsyncSession, course_id: uuid.UUID, payload: AdminModuleWrite
) -> AdminModuleItem:
    repo = LearningRepository(db)
    if await repo.get_course_by_id(course_id) is None:
        raise NotFoundException(_COURSE_NOT_FOUND)
    module = CourseModule(course_id=course_id, **payload.model_dump())
    repo.add(module)
    await _commit_or_conflict(db, _ORDER_TAKEN)
    await db.refresh(module)
    return _to_module_item(module, [])


async def update_module(
    db: AsyncSession, module_id: uuid.UUID, payload: AdminModuleWrite
) -> AdminModuleItem:
    repo = LearningRepository(db)
    module = await repo.get_module(module_id)
    if module is None:
        raise NotFoundException(_MODULE_NOT_FOUND)
    for field, value in payload.model_dump().items():
        setattr(module, field, value)
    await _commit_or_conflict(db, _ORDER_TAKEN)
    await db.refresh(module)
    lessons = await repo.list_lessons_for_modules([module.id])
    return _to_module_item(module, lessons)


async def create_lesson(
    db: AsyncSession, module_id: uuid.UUID, payload: AdminLessonWrite
) -> AdminLessonItem:
    repo = LearningRepository(db)
    if await repo.get_module(module_id) is None:
        raise NotFoundException(_MODULE_NOT_FOUND)
    lesson = Lesson(module_id=module_id, **payload.model_dump())
    repo.add(lesson)
    await _commit_or_conflict(db, _ORDER_TAKEN)
    await db.refresh(lesson)
    return AdminLessonItem.model_validate(lesson, from_attributes=True)


async def update_lesson(
    db: AsyncSession, lesson_id: uuid.UUID, payload: AdminLessonWrite
) -> AdminLessonItem:
    repo = LearningRepository(db)
    lesson = await repo.get_lesson(lesson_id)
    if lesson is None:
        raise NotFoundException(_LESSON_NOT_FOUND)
    for field, value in payload.model_dump().items():
        setattr(lesson, field, value)
    await _commit_or_conflict(db, _ORDER_TAKEN)
    await db.refresh(lesson)
    return AdminLessonItem.model_validate(lesson, from_attributes=True)


# --- helpers ------------------------------------------------------------------


async def _commit_or_conflict(db: AsyncSession, message: str) -> None:
    """Commita, traduzindo violação de UNIQUE (slug, ordem) em 409 legível.

    As UniqueConstraints são a fonte de verdade — checar antes em Python
    deixaria uma janela de corrida entre dois admins salvando ao mesmo tempo.
    """
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictException(message) from exc


async def _build_detail(repo: LearningRepository, course: Course) -> AdminCourseDetail:
    modules = await repo.list_modules(course.id)
    lessons = await repo.list_lessons_for_modules([m.id for m in modules])
    by_module: dict[uuid.UUID, list[Lesson]] = {}
    for lesson in lessons:
        by_module.setdefault(lesson.module_id, []).append(lesson)

    module_items = [_to_module_item(m, by_module.get(m.id, [])) for m in modules]
    base = _to_course_item(course, (len(modules), len(lessons)))
    return AdminCourseDetail(**base.model_dump(), modules=module_items)


def _to_course_item(course: Course, counts: tuple[int, int]) -> AdminCourseItem:
    module_count, lesson_count = counts
    return AdminCourseItem(
        id=course.id,
        slug=course.slug,
        title=course.title,
        description=course.description,
        audience=course.audience,
        thumbnail_url=course.thumbnail_url,
        is_active=course.is_active,
        module_count=module_count,
        lesson_count=lesson_count,
        updated_at=course.updated_at,
    )


def _to_module_item(module: CourseModule, lessons: list[Lesson]) -> AdminModuleItem:
    return AdminModuleItem(
        id=module.id,
        course_id=module.course_id,
        title=module.title,
        description=module.description,
        order=module.order,
        lessons=[
            AdminLessonItem.model_validate(lesson, from_attributes=True) for lesson in lessons
        ],
    )
