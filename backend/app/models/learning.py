"""Models SQLAlchemy do módulo de Videoaulas (Formação de Pais / Preparação do Aluno).

Agregado de catálogo — `Course` → `CourseModule` → `Lesson` — mais o progresso
individual `LessonProgress`. Um arquivo só, mesmo padrão de `simulado.py`:
as três entidades de catálogo não fazem sentido separadas.

**Por que o progresso é por `user_id`, não por `candidate_profile_id`**: todo
progresso do produto até aqui (`MissionProgress`, `CandidateAchievement`,
`SimuladoAttempt`) é preso ao `CandidateProfile` — e o responsável **não tem
um**. `User` é a única entidade que os quatro papéis compartilham, e é o que
faz este mesmo modelo servir a Formação de Pais hoje e a Preparação do Aluno
amanhã, sem fork.

**`audience` = nome do papel**: o vocabulário de público do curso é o mesmo
de `User.role` (`guardian`, `candidate`) de propósito — nenhuma taxonomia
nova para manter em sincronia, e a autorização vira uma comparação direta
(`course.audience == user.role`) validada no service, nunca só no front.

**Origem do vídeo abstraída** (`video_provider` + `video_ref`): a UI resolve
o provedor num único ponto (`resolveVideoSource()`), então trocar a
hospedagem depois não reescreve componente nenhum. Só `url` (arquivo direto,
`<video>` nativo) está implementado — é o único que consegue reportar a
posição exata para o "continuar de onde parou". YouTube via iframe não
reporta posição sem a IFrame API (uma biblioteca a mais), por isso ficou de
fora até haver necessidade real.
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin
from app.models.user import ROLE_CANDIDATE, ROLE_GUARDIAN

CourseAudience = Literal["guardian", "candidate"]
#: Públicos válidos = exatamente os papéis que consomem conteúdo. Coordenador e
#: admin não têm curso próprio; enxergam todos pela gestão.
VALID_AUDIENCES: Final = (ROLE_GUARDIAN, ROLE_CANDIDATE)

VideoProvider = Literal["url"]
PROVIDER_URL: Final = "url"
VALID_PROVIDERS: Final = (PROVIDER_URL,)
# `f"{VALID_PROVIDERS}"` renderizaria `('url',)` — vírgula final é SQL
# inválido numa tupla de 1 elemento (os outros CHECKs do projeto têm ≥2 e
# nunca tropeçaram nisso). Montado explicitamente.
_PROVIDERS_SQL: Final = "(" + ", ".join(f"'{p}'" for p in VALID_PROVIDERS) + ")"

#: Fração assistida a partir da qual a aula conta como concluída. Não é 100%
#: de propósito: ninguém assiste os créditos, e exigir o último segundo
#: deixaria aulas eternamente "em andamento" por causa de um scrub.
COMPLETION_THRESHOLD: Final = 0.9


class Course(Base, TimestampMixin):
    """Um curso inteiro, dirigido a um público (papel) específico."""

    __tablename__ = "courses"
    __table_args__ = (CheckConstraint(f"audience IN {VALID_AUDIENCES}", name="ck_course_audience"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    #: Chave natural estável para URL e para o seed idempotente
    #: (ex.: `formacao-de-pais`). Nunca muda depois de publicado.
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[CourseAudience] = mapped_column(String(20), index=True, nullable=False)
    #: Opcional e pequena (o front faz lazy-load). `None` = card sem imagem.
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    def __repr__(self) -> str:
        return f"<Course slug={self.slug} audience={self.audience}>"


class CourseModule(Base, TimestampMixin):
    """Um capítulo do curso — só agrupa e ordena aulas."""

    __tablename__ = "course_modules"
    __table_args__ = (UniqueConstraint("course_id", "order", name="uq_course_module_order"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<CourseModule course_id={self.course_id} order={self.order}>"


class Lesson(Base, TimestampMixin):
    """Uma videoaula dentro de um módulo."""

    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("module_id", "order", name="uq_lesson_order"),
        CheckConstraint(f"video_provider IN {_PROVIDERS_SQL}", name="ck_lesson_video_provider"),
        CheckConstraint("duration_seconds > 0", name="ck_lesson_duration"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("course_modules.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_provider: Mapped[VideoProvider] = mapped_column(
        String(20), default=PROVIDER_URL, server_default=PROVIDER_URL, nullable=False
    )
    #: O que o provedor precisa para reproduzir. Para `url`, a URL do arquivo.
    video_ref: Mapped[str] = mapped_column(String(1000), nullable=False)
    #: Necessário para o percentual assistido e para exibir "⏱ 12 min" sem
    #: precisar carregar o vídeo — que é exatamente o que não pode acontecer
    #: na listagem (página leve, vídeo só sob demanda).
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    def __repr__(self) -> str:
        return f"<Lesson module_id={self.module_id} order={self.order}>"


class LessonProgress(Base, TimestampMixin):
    """Progresso de uma pessoa (qualquer papel) numa aula."""

    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"),
        CheckConstraint("position_seconds >= 0", name="ck_lesson_progress_position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    #: Última posição conhecida — é o "continuar de 07:00". Nunca regride por
    #: causa de um scrub para trás: o service guarda o máximo, não o último.
    position_seconds: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    #: `None` = ainda não cruzou o `COMPLETION_THRESHOLD`.
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<LessonProgress user_id={self.user_id} lesson_id={self.lesson_id}>"
