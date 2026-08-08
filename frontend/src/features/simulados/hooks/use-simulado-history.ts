"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchSimuladoHistory } from "@/features/simulados/services/simulado.service";

export const SIMULADO_HISTORY_QUERY_KEY = ["simulados", "history"] as const;

/** Busca o histórico pessoal de simulados (`GET /api/v1/simulados/history`). */
export function useSimuladoHistory() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: SIMULADO_HISTORY_QUERY_KEY,
    queryFn: fetchSimuladoHistory,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
