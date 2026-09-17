"""Teste de integração da gestão de cursos (`admin_learning_service`).

Cobre o ciclo criar → editar → listar em cada nível (curso, módulo, aula)
e as duas colisões que o admin vai esbarrar na prática: slug repetido e
ordem repetida — ambas devolvem 409 com mensagem, nunca um 500 de
IntegrityError vazando para a tela.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.schemas.admin_learning import AdminCourseWrite, AdminLessonWrite, AdminModuleWrite
from app.services import admin_learning_service

_MOCK_VIDEO = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"


def _course_payload(**overrides) -> AdminCourseWrite:
    base = {
        "slug": f"curso-{uuid.uuid4().hex[:8]}",
        "title": "Curso de Teste",
        "description": "Descrição de teste.",
        "audience": "guardian",
    }
    return AdminCourseWrite(**{**base, **overrides})


def _lesson_payload(order: int = 1) -> AdminLessonWrite:
    return AdminLessonWrite(
        title=f"Aula {order}", video_ref=_MOCK_VIDEO, duration_seconds=100, order=order
    )


async def test_cria_e_lista_curso_com_contagens(db_session: AsyncSession) -> None:
    created = await admin_learning_service.create_course(db_session, _course_payload())
    assert created.module_count == 0

    module = await admin_learning_service.create_module(
        db_session, created.id, AdminModuleWrite(title="Módulo 1", order=1)
    )
    await admin_learning_service.create_lesson(db_session, module.id, _lesson_payload(1))
    await admin_learning_service.create_lesson(db_session, module.id, _lesson_payload(2))

    listed = await admin_learning_service.list_courses(db_session)
    row = next(c for c in listed.courses if c.id == created.id)
    assert (row.module_count, row.lesson_count) == (1, 2)


async def test_detalhe_traz_a_arvore_completa(db_session: AsyncSession) -> None:
    course = await admin_learning_service.create_course(db_session, _course_payload())
    module = await admin_learning_service.create_module(
        db_session, course.id, AdminModuleWrite(title="M1", order=1)
    )
    await admin_learning_service.create_lesson(db_session, module.id, _lesson_payload(1))

    detail = await admin_learning_service.get_course_detail(db_session, course.id)

    assert len(detail.modules) == 1
    assert len(detail.modules[0].lessons) == 1
    assert detail.modules[0].lessons[0].video_ref == _MOCK_VIDEO


async def test_slug_duplicado_devolve_conflito(db_session: AsyncSession) -> None:
    payload = _course_payload()
    await admin_learning_service.create_course(db_session, payload)

    with pytest.raises(ConflictException):
        await admin_learning_service.create_course(db_session, payload)


async def test_ordem_duplicada_de_aula_devolve_conflito(db_session: AsyncSession) -> None:
    """Regra que o `UniqueConstraint` garante; o service só traduz para 409."""
    course = await admin_learning_service.create_course(db_session, _course_payload())
    module = await admin_learning_service.create_module(
        db_session, course.id, AdminModuleWrite(title="M1", order=1)
    )
    await admin_learning_service.create_lesson(db_session, module.id, _lesson_payload(1))

    with pytest.raises(ConflictException):
        await admin_learning_service.create_lesson(db_session, module.id, _lesson_payload(1))


async def test_reordenar_e_editar_a_ordem(db_session: AsyncSession) -> None:
    course = await admin_learning_service.create_course(db_session, _course_payload())
    module = await admin_learning_service.create_module(
        db_session, course.id, AdminModuleWrite(title="M1", order=1)
    )
    lesson = await admin_learning_service.create_lesson(db_session, module.id, _lesson_payload(1))

    updated = await admin_learning_service.update_lesson(
        db_session,
        lesson.id,
        AdminLessonWrite(title="Aula 1", video_ref=_MOCK_VIDEO, duration_seconds=100, order=5),
    )

    assert updated.order == 5


async def test_desativar_curso_some_do_publico_mas_fica_na_gestao(
    db_session: AsyncSession,
) -> None:
    course = await admin_learning_service.create_course(db_session, _course_payload())
    await admin_learning_service.update_course(
        db_session, course.id, _course_payload(slug=course.slug, is_active=False)
    )

    listed = await admin_learning_service.list_courses(db_session)
    row = next(c for c in listed.courses if c.id == course.id)
    assert row.is_active is False


async def test_editar_curso_inexistente_levanta_not_found(db_session: AsyncSession) -> None:
    with pytest.raises(NotFoundException):
        await admin_learning_service.update_course(db_session, uuid.uuid4(), _course_payload())


def test_slug_e_normalizado_e_validado() -> None:
    assert _course_payload(slug="  Formacao-De-Pais ").slug == "formacao-de-pais"
    with pytest.raises(ValueError):
        _course_payload(slug="com espaço")
    with pytest.raises(ValueError):
        _course_payload(slug="-comeca-com-hifen")
