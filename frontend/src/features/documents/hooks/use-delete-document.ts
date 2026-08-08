"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DOCUMENTS_QUERY_KEY } from "@/features/documents/hooks/use-documents";
import { deleteDocument } from "@/features/documents/services/document.service";

/** Remove um documento enviado (`DELETE /api/v1/documents/{tipo}`), para reenviar do zero. */
export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DOCUMENTS_QUERY_KEY });
      toast.success("Documento removido");
    },
    onError: (error) => {
      toast.error("Não foi possível remover o documento", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
