"""Contrato da gestão de cursos no painel admin (`/admin/learning/*`).

Escrita e leitura separadas, como em `reward.py`: `*Write` é o que o
formulário envia (validado na borda), `Admin*Item` é o que a tela lista.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.learning import (
    COMPLETION_THRESHOLD,
    VALID_AUDIENCES,
    VALID_PROVIDERS,
    CourseAudience,
    VideoProvider,
)

_SLUG_HINT = "só letras minúsculas, números e hífens (ex.: formacao-de-pais)"


def _validate_slug(value: str) -> str:
    slug = value.strip().lower()
    if not slug or not all(ch.isalnum() or ch == "-" for ch in slug) or slug != slug.strip("-"):
        raise ValueError(f"Slug inválido — {_SLUG_HINT}.")
    return slug


# --- Escrita ------------------------------------------------------------------


class AdminCourseWrite(BaseModel):
    slug: str = Field(min_length=2, max_length=80, description=_SLUG_HINT)
    title: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=1)
    audience: CourseAudience
    thumbnail_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True

    @field_validator("slug")
    @classmethod
    def _slug(cls, value: str) -> str:
        return _validate_slug(value)

    @field_validator("audience")
    @classmethod
    def _audience(cls, value: str) -> str:
        if value not in VALID_AUDIENCES:
            raise ValueError(f"Público inválido. Use um de: {', '.join(VALID_AUDIENCES)}.")
        return value


class AdminModuleWrite(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    description: str | None = None
    order: int = Field(ge=1)


class AdminLessonWrite(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    description: str | None = None
    video_provider: VideoProvider = "url"
    video_ref: str = Field(min_length=1, max_length=1000)
    duration_seconds: int = Field(gt=0, description="Duração real do vídeo, em segundos.")
    order: int = Field(ge=1)
    is_active: bool = True

    @field_validator("video_provider")
    @classmethod
    def _provider(cls, value: str) -> str:
        if value not in VALID_PROVIDERS:
            raise ValueError(f"Provedor inválido. Use um de: {', '.join(VALID_PROVIDERS)}.")
        return value


# --- Leitura ------------------------------------------------------------------


class AdminLessonItem(BaseModel):
    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    description: str | None
    video_provider: VideoProvider
    video_ref: str
    duration_seconds: int
    order: int
    is_active: bool


class AdminModuleItem(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    description: str | None
    order: int
    lessons: list[AdminLessonItem]


class AdminCourseItem(BaseModel):
    """Um curso na lista de gestão — com contagens, sem a árvore inteira."""

    id: uuid.UUID
    slug: str
    title: str
    description: str
    audience: CourseAudience
    thumbnail_url: str | None
    is_active: bool
    module_count: int
    lesson_count: int
    updated_at: datetime


class AdminCourseDetail(AdminCourseItem):
    """O curso com a árvore completa — para a tela de edição."""

    modules: list[AdminModuleItem]


class AdminCourseListResponse(BaseModel):
    courses: list[AdminCourseItem]
    #: Para o formulário oferecer só os públicos válidos.
    audiences: list[str]
    providers: list[str]
    #: Informativo: o admin precisa saber que a duração cadastrada decide
    #: quando a aula conta como concluída.
    completion_threshold: float = COMPLETION_THRESHOLD
