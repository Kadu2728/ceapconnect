"""Model SQLAlchemy da entidade `CandidateDocument` (EPIC 15 — Upload de documentos).

Documento enviado pelo candidato (identidade, comprovante de residência, foto)
para a etapa de Documentação da jornada — a própria predição de evasão (EPIC
14) identificou esta etapa como o principal ponto de travamento, então dar ao
candidato um jeito real de enviar o documento (em vez de um passo só
informativo) ataca a causa, não o sintoma.

**Armazenamento**: `bytea` direto no Postgres (Neon), sem serviço de storage
externo — decisão deliberada para o candidato conseguir enviar o documento
hoje, sem depender de nenhuma conta nova de terceiros ser criada antes. Com o
limite de 2MB/arquivo e 3 tipos de documento (ver `document_service.py`), o
volume é tranquilo para a escala atual. Se crescer muito, migrar para object
storage (S3/Cloudinary) é uma evolução de infraestrutura, não uma reescrita.

Um documento por (candidato, tipo) — reenviar substitui o anterior.
"""

import uuid
from datetime import datetime
from typing import Final, Literal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

DocumentType = Literal["documento_identidade", "comprovante_residencia", "foto_3x4"]

DOC_IDENTIDADE: Final = "documento_identidade"
DOC_COMPROVANTE_RESIDENCIA: Final = "comprovante_residencia"
DOC_FOTO_3X4: Final = "foto_3x4"

_VALID_DOCUMENT_TYPES: Final = (DOC_IDENTIDADE, DOC_COMPROVANTE_RESIDENCIA, DOC_FOTO_3X4)

# Export público: usado por `app.services.journey_service` para saber quantos
# documentos completam a etapa "Documentação" da jornada, sem duplicar a
# lista em outro módulo.
REQUIRED_DOCUMENT_TYPES: Final = _VALID_DOCUMENT_TYPES


class CandidateDocument(Base):
    """Um documento enviado pelo candidato para um tipo específico do checklist."""

    __tablename__ = "candidate_documents"
    __table_args__ = (
        CheckConstraint(
            f"document_type IN {_VALID_DOCUMENT_TYPES}", name="ck_candidate_document_type"
        ),
        UniqueConstraint(
            "candidate_profile_id", "document_type", name="uq_candidate_document_profile_type"
        ),
    )

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
    document_type: Mapped[DocumentType] = mapped_column(String(40), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<CandidateDocument candidate_profile_id={self.candidate_profile_id} "
            f"document_type={self.document_type}>"
        )
