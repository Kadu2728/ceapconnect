/**
 * Contratos do Upload de Documentos (EPIC 15), espelhando o backend
 * (`/api/v1/documents`). Campos em `snake_case` como o backend os envia.
 */

export type DocumentType = "documento_identidade" | "comprovante_residencia" | "foto_3x4";

export interface DocumentItem {
  document_type: DocumentType;
  label: string;
  description: string;
  uploaded: boolean;
  file_name: string | null;
  file_size: number | null;
  uploaded_at: string | null;
}

export interface DocumentChecklist {
  documents: DocumentItem[];
  total_required: number;
  total_uploaded: number;
  all_complete: boolean;
}
