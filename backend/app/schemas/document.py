"""Schemas Pydantic do Upload de Documentos (EPIC 15).

Contrato de:
- `GET    /api/v1/documents`                    → checklist do candidato;
- `POST   /api/v1/documents/{document_type}`    → envia/substitui um documento;
- `DELETE /api/v1/documents/{document_type}`    → remove um documento enviado.

O arquivo em si nunca aparece num destes schemas (é `bytea` no banco, servido
por um endpoint de download dedicado) — aqui só trafega metadado.
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.candidate_document import DocumentType


class DocumentItem(BaseModel):
    """Um item do checklist de documentos, com o status de envio do candidato."""

    document_type: DocumentType
    label: str
    description: str
    uploaded: bool
    file_name: str | None
    file_size: int | None
    uploaded_at: datetime | None


class DocumentChecklistResponse(BaseModel):
    """Payload de `GET /api/v1/documents`."""

    documents: list[DocumentItem]
    total_required: int
    total_uploaded: int
    all_complete: bool
