"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { DOCUMENTS_QUERY_KEY } from "@/features/documents/hooks/use-documents";
import { uploadDocument } from "@/features/documents/services/document.service";
import type { DocumentType } from "@/features/documents/types/document.types";

interface UploadArgs {
  documentType: DocumentType;
  file: File;
}

/**
 * Envia um documento (`POST /api/v1/documents/{tipo}`). Invalida o checklist
 * e o dashboard — o upload também alimenta o modelo de risco (EPIC 14), então
 * a jornada exibida pode refletir o avanço.
 */
export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ documentType, file }: UploadArgs) =>
      uploadDocument(documentType, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DOCUMENTS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
      toast.success("Documento enviado com sucesso!");
    },
    onError: (error) => {
      toast.error("Não foi possível enviar o documento", {
        description: extractApiErrorMessage(
          error,
          "Confira o arquivo e tente novamente.",
        ),
      });
    },
  });
}
