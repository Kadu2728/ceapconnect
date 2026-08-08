"""Acesso a dados da entidade `CandidateDocument` (EPIC 15 — Upload de documentos).

Isola toda query relacionada a documentos — a camada de services nunca deve
montar SQL/ORM diretamente.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_document import CandidateDocument, DocumentType


class CandidateDocumentRepository:
    """Repositório de leitura/escrita dos documentos enviados por candidato."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get(
        self, *, candidate_profile_id: uuid.UUID, document_type: DocumentType
    ) -> CandidateDocument | None:
        """Busca o documento de um tipo específico do candidato (ou None)."""
        stmt = select(CandidateDocument).where(
            CandidateDocument.candidate_profile_id == candidate_profile_id,
            CandidateDocument.document_type == document_type,
        )
        return (await self._db.execute(stmt)).scalar_one_or_none()

    async def list_for_profile(self, candidate_profile_id: uuid.UUID) -> list[CandidateDocument]:
        """Todos os documentos já enviados pelo candidato."""
        stmt = select(CandidateDocument).where(
            CandidateDocument.candidate_profile_id == candidate_profile_id
        )
        return list((await self._db.execute(stmt)).scalars().all())

    async def upsert(
        self,
        *,
        candidate_profile_id: uuid.UUID,
        document_type: DocumentType,
        file_name: str,
        mime_type: str,
        file_size: int,
        file_data: bytes,
    ) -> CandidateDocument:
        """Cria ou substitui o documento deste tipo (flush, sem commit).

        Reenviar um documento sempre substitui o anterior — o candidato só
        precisa da versão mais recente de cada tipo, nunca um histórico.
        """
        existing = await self.get(
            candidate_profile_id=candidate_profile_id, document_type=document_type
        )
        if existing is None:
            existing = CandidateDocument(
                candidate_profile_id=candidate_profile_id, document_type=document_type
            )
            self._db.add(existing)

        existing.file_name = file_name
        existing.mime_type = mime_type
        existing.file_size = file_size
        existing.file_data = file_data
        await self._db.flush()
        return existing

    async def delete(self, document: CandidateDocument) -> None:
        """Remove um documento (flush, sem commit)."""
        await self._db.delete(document)
        await self._db.flush()
