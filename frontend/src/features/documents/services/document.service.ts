import { apiClient } from "@/lib/axios";

import type {
  DocumentChecklist,
  DocumentItem,
  DocumentType,
} from "@/features/documents/types/document.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Documentos — única camada autorizada a falar com
 * `apiClient` neste domínio.
 */
const DOCUMENTS_ENDPOINT = "/api/v1/documents";

export async function fetchDocumentChecklist(): Promise<DocumentChecklist> {
  const { data } =
    await apiClient.get<ApiEnvelope<DocumentChecklist>>(DOCUMENTS_ENDPOINT);
  return data.data;
}

export async function uploadDocument(
  documentType: DocumentType,
  file: File,
): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post<ApiEnvelope<DocumentItem>>(
    `${DOCUMENTS_ENDPOINT}/${documentType}`,
    formData,
    // A instância do axios tem `Content-Type: application/json` por padrão;
    // para `FormData` isso precisa ser removido explicitamente (`undefined`)
    // para o navegador montar sozinho o boundary correto do multipart — um
    // Content-Type fixo aqui quebraria o parsing do arquivo no backend.
    { headers: { "Content-Type": undefined } },
  );
  return data.data;
}

export async function deleteDocument(documentType: DocumentType): Promise<void> {
  await apiClient.delete(`${DOCUMENTS_ENDPOINT}/${documentType}`);
}

export async function fetchDocumentFileUrl(documentType: DocumentType): Promise<string> {
  const { data } = await apiClient.get(`${DOCUMENTS_ENDPOINT}/${documentType}/file`, {
    responseType: "blob",
  });
  return URL.createObjectURL(data as Blob);
}
