"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import {
  fetchRiskQueue,
  type FetchRiskQueueParams,
} from "@/features/risk/services/risk.service";

export const RISK_QUEUE_QUERY_KEY = ["risk", "queue"] as const;

/**
 * Busca a fila priorizada de risco (`GET /admin/risk/queue`). Só executa
 * quando a store reidratou, há token, e o usuário é coordenador ou admin —
 * evita uma chamada que o backend recusaria com 403 para candidatos comuns.
 */
export function useRiskQueue(params: FetchRiskQueueParams = {}) {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);
  const isAdmin = useAuthStore((state) => state.user?.is_admin ?? false);
  const role = useAuthStore((state) => state.user?.role ?? "candidate");
  const isStaff = isAdmin || role === "coordinator";

  return useQuery({
    queryKey: [...RISK_QUEUE_QUERY_KEY, params],
    queryFn: () => fetchRiskQueue(params),
    enabled: hasHydrated && Boolean(accessToken) && isStaff,
  });
}
