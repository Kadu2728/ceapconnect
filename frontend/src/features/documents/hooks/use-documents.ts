"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchDocumentChecklist } from "@/features/documents/services/document.service";

export const DOCUMENTS_QUERY_KEY = ["documents"] as const;

/**
 * Busca o checklist de documentos do candidato (`GET /api/v1/documents`).
 * Mesmo guard de sessão do Dashboard.
 */
export function useDocuments() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: DOCUMENTS_QUERY_KEY,
    queryFn: fetchDocumentChecklist,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
