"""Regra de negócio do Upload de Documentos (EPIC 15).

Checklist de documentos exigidos na etapa de Documentação da jornada — a
predição de evasão (EPIC 14) identificou esta etapa como o principal ponto de
travamento; dar ao candidato um jeito real de enviar o documento (em vez de um
passo só informativo) ataca a causa raiz.

Cada envio bem-sucedido registra um `document_uploaded` (EPIC 14 já usa este
evento para decidir se o candidato está "travado" numa etapa bloqueante) —
então o próprio upload já realimenta o modelo de risco.
"""

import uuid
from typing import Final

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.activity_event import EVENT_DOCUMENT_UPLOADED
from app.models.candidate_document import (
    DOC_COMPROVANTE_RESIDENCIA,
    DOC_FOTO_3X4,
    DOC_IDENTIDADE,
    CandidateDocument,
    DocumentType,
)
from app.models.user import User
from app.repositories.candidate_document_repository import CandidateDocumentRepository
from app.schemas.document import DocumentChecklistResponse, DocumentItem
from app.services import activity_event_service
from app.services.candidate_profile_service import get_profile_or_raise

# Catálogo dos documentos exigidos — mesmo padrão de "catálogo em código, não
# em tabela" usado pelos níveis de gamificação (`app/core/gamification.py`):
# a lista muda pouco e não precisa de CRUD/migration para ser ajustada.
_DOCUMENT_CATALOG: Final = (
    {
        "type": DOC_IDENTIDADE,
        "label": "Documento de identidade",
        "description": "RG ou Certidão de Nascimento (frente e verso, foto legível).",
    },
    {
        "type": DOC_COMPROVANTE_RESIDENCIA,
        "label": "Comprovante de residência",
        "description": "Conta de luz, água ou telefone recente, em nome do responsável.",
    },
    {
        "type": DOC_FOTO_3X4,
        "label": "Foto 3x4",
        "description": "Foto recente, com fundo neutro, para o cadastro.",
    },
)
_DOCUMENT_LABELS: Final = {item["type"]: item["label"] for item in _DOCUMENT_CATALOG}

_MAX_FILE_SIZE_BYTES: Final = 2 * 1024 * 1024  # 2MB — imagem de celular comprimida cabe tranquilo.
_ALLOWED_MIME_TYPES: Final = {"image/jpeg", "image/png", "application/pdf"}


async def list_documents(db: AsyncSession, user: User) -> DocumentChecklistResponse:
    """Checklist de documentos do candidato: exigidos × já enviados."""
    profile = await get_profile_or_raise(db, user)
    uploaded = {
        doc.document_type: doc
        for doc in await CandidateDocumentRepository(db).list_for_profile(profile.id)
    }

    items = [
        DocumentItem(
            document_type=entry["type"],
            label=entry["label"],
            description=entry["description"],
            uploaded=entry["type"] in uploaded,
            file_name=uploaded[entry["type"]].file_name if entry["type"] in uploaded else None,
            file_size=uploaded[entry["type"]].file_size if entry["type"] in uploaded else None,
            uploaded_at=(
                uploaded[entry["type"]].uploaded_at if entry["type"] in uploaded else None
            ),
        )
        for entry in _DOCUMENT_CATALOG
    ]

    total_uploaded = sum(1 for item in items if item.uploaded)
    return DocumentChecklistResponse(
        documents=items,
        total_required=len(items),
        total_uploaded=total_uploaded,
        all_complete=total_uploaded == len(items),
    )


async def upload_document(
    db: AsyncSession, user: User, document_type: DocumentType, file: UploadFile
) -> DocumentItem:
    """Envia (ou substitui) um documento. Valida tipo, tamanho e formato.

    Reenviar sempre registra um novo `document_uploaded` — o candidato pode
    ter corrigido um envio ruim, e cada tentativa é um sinal real de esforço.
    """
    if document_type not in _DOCUMENT_LABELS:
        raise BadRequestException("Tipo de documento inválido.")

    if file.content_type not in _ALLOWED_MIME_TYPES:
        raise BadRequestException("Formato não suportado. Envie uma foto (JPG/PNG) ou um PDF.")

    data = await file.read()
    if len(data) > _MAX_FILE_SIZE_BYTES:
        raise BadRequestException("Arquivo maior que 2MB. Envie uma versão mais leve.")
    if len(data) == 0:
        raise BadRequestException("Arquivo vazio.")

    profile = await get_profile_or_raise(db, user)
    document = await CandidateDocumentRepository(db).upsert(
        candidate_profile_id=profile.id,
        document_type=document_type,
        file_name=file.filename or "documento",
        mime_type=file.content_type,
        file_size=len(data),
        file_data=data,
    )

    await activity_event_service.track(
        db,
        candidate_profile_id=profile.id,
        name=EVENT_DOCUMENT_UPLOADED,
        props={"document_type": document_type},
    )
    await db.commit()

    return DocumentItem(
        document_type=document.document_type,
        label=_DOCUMENT_LABELS[document.document_type],
        description=next(
            e["description"] for e in _DOCUMENT_CATALOG if e["type"] == document.document_type
        ),
        uploaded=True,
        file_name=document.file_name,
        file_size=document.file_size,
        uploaded_at=document.uploaded_at,
    )


async def delete_document(db: AsyncSession, user: User, document_type: DocumentType) -> None:
    """Remove um documento enviado (ex.: candidato quer reenviar do zero)."""
    profile = await get_profile_or_raise(db, user)
    repo = CandidateDocumentRepository(db)
    document = await repo.get(candidate_profile_id=profile.id, document_type=document_type)
    if document is None:
        raise NotFoundException("Documento não encontrado.")

    await repo.delete(document)
    await db.commit()


async def get_document_file(
    db: AsyncSession, user: User, document_type: DocumentType
) -> CandidateDocument:
    """Busca o arquivo do próprio candidato (para visualizar o que enviou)."""
    profile = await get_profile_or_raise(db, user)
    document = await CandidateDocumentRepository(db).get(
        candidate_profile_id=profile.id, document_type=document_type
    )
    if document is None:
        raise NotFoundException("Documento não encontrado.")
    return document


async def get_document_file_for_candidate(
    db: AsyncSession, candidate_profile_id: uuid.UUID, document_type: DocumentType
) -> CandidateDocument:
    """Busca o arquivo de um candidato específico (uso administrativo — EPIC 14/15).

    Sem checagem de escopo aqui de propósito: quem chama (`admin_risk.py`) já
    resolve e valida o `CohortScope` antes — mantém a regra de acesso num
    único lugar.
    """
    document = await CandidateDocumentRepository(db).get(
        candidate_profile_id=candidate_profile_id, document_type=document_type
    )
    if document is None:
        raise NotFoundException("Documento não encontrado.")
    return document
