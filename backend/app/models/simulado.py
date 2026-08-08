"""Models SQLAlchemy dos Simulados de prova (EPIC 16 — candidate experience).

Preparação real para o formato do exame do CEAP (Português + Matemática,
questões objetivas — ver `USER_FLOW.md`/landing: "20 questões objetivas em
cerca de 1 hora"). Diferente do processo seletivo em si, o feedback aqui é
imediato e pessoal — é uma ferramenta de estudo, não uma avaliação com peso.

Três entidades:
- `SimuladoQuestion`: catálogo de questões (populado via seed, mesmo padrão
  de `Mission`/`Achievement` — nunca editado via CRUD administrativo nesta fase).
- `SimuladoAttempt`: uma tentativa do candidato (nasce ao iniciar, fecha ao
  finalizar). Sem uma tabela de "questões da tentativa": o conjunto sorteado é
  devolvido ao frontend em `simulado_service.start_attempt` e cada resposta é
  registrada por `question_id` — resgatar uma tentativa abandonada no meio não
  é suportado nesta fase (o candidato recomeça), simplificação deliberada.
- `SimuladoAnswer`: cada resposta dada dentro de uma tentativa.
"""

import uuid
from datetime import datetime
from typing import Any, Final, Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

SimuladoSubject = Literal["portugues", "matematica"]

SUBJECT_PORTUGUES: Final = "portugues"
SUBJECT_MATEMATICA: Final = "matematica"
_VALID_SUBJECTS: Final = (SUBJECT_PORTUGUES, SUBJECT_MATEMATICA)


class SimuladoQuestion(Base):
    """Uma questão de múltipla escolha do banco de simulados."""

    __tablename__ = "simulado_questions"
    __table_args__ = (
        CheckConstraint(f"subject IN {_VALID_SUBJECTS}", name="ck_simulado_question_subject"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    subject: Mapped[SimuladoSubject] = mapped_column(String(20), index=True, nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    # [{"key": "a", "text": "..."}, {"key": "b", "text": "..."}, ...]
    options: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    correct_option_key: Mapped[str] = mapped_column(String(5), nullable=False)
    # Mostrada ao candidato logo após responder — é o valor pedagógico do simulado.
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<SimuladoQuestion id={self.id} subject={self.subject}>"


class SimuladoAttempt(Base):
    """Uma tentativa de simulado do candidato."""

    __tablename__ = "simulado_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    # Preenchido só em `finish` — None enquanto a tentativa está em andamento.
    correct_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<SimuladoAttempt id={self.id} candidate_profile_id={self.candidate_profile_id}>"


class SimuladoAnswer(Base):
    """Uma resposta dada pelo candidato dentro de uma tentativa."""

    __tablename__ = "simulado_answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_simulado_answer_attempt_question"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("simulado_attempts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("simulado_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_option_key: Mapped[str] = mapped_column(String(5), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<SimuladoAnswer attempt_id={self.attempt_id} question_id={self.question_id}>"
