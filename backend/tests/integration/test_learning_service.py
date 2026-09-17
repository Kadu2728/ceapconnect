"""Teste de integração do módulo de Videoaulas (`learning_service`).

O teste central que o brief exige: *"o usuário não deve conseguir acessar
conteúdo destinado a outro perfil simplesmente alterando uma URL"* — e a
autorização tem que estar no backend, não só no front.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.learning import Course, CourseModule, Lesson
from app.models.user import ROLE_CANDIDATE, ROLE_GUARDIAN, User
from app.repositories.user_repository import UserRepository
from app.services import learning_service

_MOCK_VIDEO = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"


async def _course(
    db: AsyncSession, *, audience: str, lesson_count: int = 3
) -> tuple[Course, list[Lesson]]:
    """Um curso isolado por slug único, com um módulo e N aulas de 100s."""
    course = Course(
        slug=f"teste-{uuid.uuid4().hex[:8]}",
        title="Curso de Teste",
        description="Conteúdo de teste.",
        audience=audience,
    )
    db.add(course)
    await db.flush()
    module = CourseModule(course_id=course.id, title="Módulo 1", order=1)
    db.add(module)
    await db.flush()
    lessons = [
        Lesson(
            module_id=module.id,
            title=f"Aula {i}",
            video_ref=_MOCK_VIDEO,
            duration_seconds=100,
            order=i,
        )
        for i in range(1, lesson_count + 1)
    ]
    db.add_all(lessons)
    await db.flush()
    return course, lessons


async def _candidate_user(db: AsyncSession, candidate_profile) -> User:
    user = await UserRepository(db).get_by_id(candidate_profile.user_id)
    assert user is not None
    assert user.role == ROLE_CANDIDATE
    return user


async def test_responsavel_ve_so_cursos_de_responsavel(
    db_session: AsyncSession, guardian_user: User
) -> None:
    guardian_course, _ = await _course(db_session, audience=ROLE_GUARDIAN)
    candidate_course, _ = await _course(db_session, audience=ROLE_CANDIDATE)

    slugs = {c.slug for c in await learning_service.list_courses(db_session, guardian_user)}

    assert guardian_course.slug in slugs
    assert candidate_course.slug not in slugs


async def test_responsavel_nao_abre_curso_de_aluno_pela_url(
    db_session: AsyncSession, guardian_user: User
) -> None:
    """O teste que o brief pede: trocar o slug na URL não dá acesso."""
    candidate_course, _ = await _course(db_session, audience=ROLE_CANDIDATE)

    with pytest.raises(ForbiddenException):
        await learning_service.get_course_overview(db_session, guardian_user, candidate_course.slug)


async def test_responsavel_nao_abre_aula_de_aluno_pelo_id(
    db_session: AsyncSession, guardian_user: User
) -> None:
    """Mesmo freio na aula individual — e antes de qualquer dado ser montado."""
    _, lessons = await _course(db_session, audience=ROLE_CANDIDATE)

    with pytest.raises(ForbiddenException):
        await learning_service.get_lesson(db_session, guardian_user, lessons[0].id)

    with pytest.raises(ForbiddenException):
        await learning_service.update_progress(db_session, guardian_user, lessons[0].id, 50)


async def test_admin_ve_qualquer_curso(db_session: AsyncSession, guardian_user: User) -> None:
    """Gestão enxerga tudo — é o que permite o painel administrar os dois públicos."""
    guardian_user.is_admin = True
    await db_session.flush()
    candidate_course, _ = await _course(db_session, audience=ROLE_CANDIDATE)

    overview = await learning_service.get_course_overview(
        db_session, guardian_user, candidate_course.slug
    )

    assert overview.course.slug == candidate_course.slug


async def test_curso_inexistente_levanta_not_found(
    db_session: AsyncSession, guardian_user: User
) -> None:
    with pytest.raises(NotFoundException):
        await learning_service.get_course_overview(db_session, guardian_user, "nao-existe")


async def test_visao_geral_nunca_carrega_o_video(
    db_session: AsyncSession, guardian_user: User
) -> None:
    """Garantia estrutural da página leve: a listagem não tem campo de vídeo."""
    course, _ = await _course(db_session, audience=ROLE_GUARDIAN)

    overview = await learning_service.get_course_overview(db_session, guardian_user, course.slug)

    serialized = overview.model_dump_json()
    assert "video_ref" not in serialized
    assert _MOCK_VIDEO not in serialized


async def test_progresso_e_proxima_aula_sao_calculados(
    db_session: AsyncSession, guardian_user: User
) -> None:
    course, lessons = await _course(db_session, audience=ROLE_GUARDIAN, lesson_count=3)

    before = await learning_service.get_course_overview(db_session, guardian_user, course.slug)
    assert before.progress_percent == 0
    assert before.next_lesson is not None
    assert before.next_lesson.id == lessons[0].id

    # Conclui a primeira aula (100s de duração, limiar de 90%).
    await learning_service.update_progress(db_session, guardian_user, lessons[0].id, 95)

    after = await learning_service.get_course_overview(db_session, guardian_user, course.slug)
    assert after.completed_lessons == 1
    assert after.progress_percent == 33
    assert after.next_lesson is not None
    assert after.next_lesson.id == lessons[1].id


async def test_aula_conclui_ao_cruzar_o_limiar_uma_unica_vez(
    db_session: AsyncSession, guardian_user: User
) -> None:
    _, lessons = await _course(db_session, audience=ROLE_GUARDIAN, lesson_count=1)
    lesson = lessons[0]

    partial = await learning_service.update_progress(db_session, guardian_user, lesson.id, 50)
    assert partial.status == "in_progress"
    assert partial.watched_percent == 50
    assert partial.just_completed is False

    crossed = await learning_service.update_progress(db_session, guardian_user, lesson.id, 91)
    assert crossed.status == "completed"
    assert crossed.just_completed is True

    # Segunda chamada acima do limiar: continua concluída, mas `just_completed`
    # é False — o front usa isso para o feedback aparecer uma vez só.
    again = await learning_service.update_progress(db_session, guardian_user, lesson.id, 100)
    assert again.status == "completed"
    assert again.just_completed is False


async def test_posicao_nunca_regride_com_scrub_para_tras(
    db_session: AsyncSession, guardian_user: User
) -> None:
    """Voltar 30s para rever um trecho não pode apagar o "continuar de"."""
    _, lessons = await _course(db_session, audience=ROLE_GUARDIAN, lesson_count=1)
    lesson = lessons[0]

    await learning_service.update_progress(db_session, guardian_user, lesson.id, 70)
    result = await learning_service.update_progress(db_session, guardian_user, lesson.id, 40)

    assert result.resume_position_seconds == 70


async def test_posicao_e_limitada_pela_duracao(
    db_session: AsyncSession, guardian_user: User
) -> None:
    """Um `timeupdate` no último frame pode passar de `duration` por
    arredondamento — isso não pode virar 130%."""
    _, lessons = await _course(db_session, audience=ROLE_GUARDIAN, lesson_count=1)

    result = await learning_service.update_progress(db_session, guardian_user, lessons[0].id, 130)

    assert result.watched_percent == 100


async def test_aula_traz_vizinhas_na_ordem_do_curso(
    db_session: AsyncSession, guardian_user: User
) -> None:
    _, lessons = await _course(db_session, audience=ROLE_GUARDIAN, lesson_count=3)

    middle = await learning_service.get_lesson(db_session, guardian_user, lessons[1].id)

    assert middle.previous_lesson_id == lessons[0].id
    assert middle.next_lesson_id == lessons[2].id
    assert middle.video_ref == _MOCK_VIDEO


async def test_candidato_ve_so_cursos_de_candidato(
    db_session: AsyncSession, candidate_profile
) -> None:
    """A mesma API serve o outro público — sem nenhuma rota nova."""
    user = await _candidate_user(db_session, candidate_profile)
    guardian_course, _ = await _course(db_session, audience=ROLE_GUARDIAN)
    candidate_course, _ = await _course(db_session, audience=ROLE_CANDIDATE)

    slugs = {c.slug for c in await learning_service.list_courses(db_session, user)}

    assert candidate_course.slug in slugs
    assert guardian_course.slug not in slugs
