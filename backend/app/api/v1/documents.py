"""Router do Upload de Documentos (EPIC 15).

Rotas protegidas via `Depends(get_current_user)`. Toda a regra de negócio
(validação de tipo/tamanho, upsert, tracking) vive em
`app.services.document_service` — o router apenas orquestra e envelopa.

O download do arquivo (`GET /{document_type}/file`) foge do envelope padrão
`ApiResponse` de propósito: é a resposta binária crua do documento, não um
payload JSON.
"""

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.candidate_document import DocumentType
from app.models.user import User
from app.schemas.document import DocumentChecklistResponse, DocumentItem
from app.schemas.response import ApiResponse
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["Documentos"])


@router.get(
    "",
    response_model=ApiResponse[DocumentChecklistResponse],
    summary="Checklist de documentos do candidato",
)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DocumentChecklistResponse]:
    """Retorna os documentos exigidos e o status de envio de cada um."""
    data = await document_service.list_documents(db, current_user)
    return ApiResponse(success=True, message="Checklist recuperado com sucesso.", data=data)


@router.post(
    "/{document_type}",
    response_model=ApiResponse[DocumentItem],
    summary="Envia (ou substitui) um documento",
)
async def upload_document(
    document_type: DocumentType,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DocumentItem]:
    """Envia um documento (JPG/PNG/PDF, até 2MB). Reenviar substitui o anterior."""
    data = await document_service.upload_document(db, current_user, document_type, file)
    return ApiResponse(success=True, message="Documento enviado com sucesso.", data=data)


@router.delete(
    "/{document_type}",
    response_model=ApiResponse[None],
    summary="Remove um documento enviado",
)
async def delete_document(
    document_type: DocumentType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Remove o documento enviado, para o candidato reenviar do zero."""
    await document_service.delete_document(db, current_user, document_type)
    return ApiResponse(success=True, message="Documento removido com sucesso.", data=None)


@router.get(
    "/{document_type}/file",
    summary="Baixa/visualiza o arquivo enviado pelo próprio candidato",
)
async def get_document_file(
    document_type: DocumentType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Retorna o arquivo binário (imagem/PDF), para o candidato conferir o que enviou."""
    document = await document_service.get_document_file(db, current_user, document_type)
    return Response(
        content=document.file_data,
        media_type=document.mime_type,
        headers={"Content-Disposition": f'inline; filename="{document.file_name}"'},
    )
