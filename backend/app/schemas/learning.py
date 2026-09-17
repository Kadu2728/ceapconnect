"""Contrato do módulo de Videoaulas (`/api/v1/learning/*`).

A listagem (`CourseOverview`) é deliberadamente leve: título, progresso,
próxima aula e os módulos com estado de cada aula — **nunca** a URL do vídeo.
Ela só sai em `LessonDetail`, quando a pessoa abre a aula. É a garantia
estrutural de que a página "Formação de Pais" não carrega vídeo nenhum.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.learning import CourseAudience, VideoProvider

LessonStatus = Literal["available", "in_progress", "completed"]


class LessonSummary(BaseModel):
    """Uma aula na listagem do curso — sem o vídeo."""

    id: uuid.UUID
    title: str
    description: str | None
    duration_seconds: int
    order: int
    status: LessonStatus
    #: 0–100, calculado de `position_seconds / duration_seconds`.
    watched_percent: int
    #: "Continuar de 07:00" — só faz sentido em `in_progress`.
    resume_position_seconds: int


class ModuleSummary(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    order: int
    lessons: list[LessonSummary]
    completed_count: int


class CourseCard(BaseModel):
    """Um curso na lista de cursos da pessoa."""

    id: uuid.UUID
    slug: str
    title: str
    description: str
    audience: CourseAudience
    thumbnail_url: str | None


class CourseOverview(BaseModel):
    """A página inteira da formação, numa resposta só."""

    course: CourseCard
    modules: list[ModuleSummary]
    total_lessons: int
    completed_lessons: int
    #: 0–100, calculado — nunca armazenado.
    progress_percent: int
    #: A primeira aula não concluída na ordem do curso, ou `None` se acabou.
    #: É a resposta para "o que eu faço agora" — o princípio central do
    #: CEAP Connect aplicado à formação.
    next_lesson: LessonSummary | None


class LessonDetail(BaseModel):
    """A aula aberta para assistir — a única resposta que carrega o vídeo."""

    id: uuid.UUID
    course_slug: str
    course_title: str
    module_title: str
    title: str
    description: str | None
    video_provider: VideoProvider
    video_ref: str
    duration_seconds: int
    status: LessonStatus
    resume_position_seconds: int
    #: Navegação sem voltar para a lista.
    previous_lesson_id: uuid.UUID | None
    next_lesson_id: uuid.UUID | None


class ProgressUpdateRequest(BaseModel):
    """Corpo de `PUT /learning/lessons/{id}/progress`."""

    position_seconds: int = Field(ge=0)


class ProgressUpdateResult(BaseModel):
    lesson_id: uuid.UUID
    status: LessonStatus
    watched_percent: int
    resume_position_seconds: int
    completed_at: datetime | None
    #: `True` só na chamada em que a aula cruzou o limiar — o front usa para
    #: mostrar o feedback de conclusão uma única vez.
    just_completed: bool
