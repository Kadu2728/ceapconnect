"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchDashboard } from "@/features/dashboard/services/dashboard.service";

export const DASHBOARD_QUERY_KEY = ["dashboard"] as const;

/**
 * Busca os dados agregados do Dashboard (`GET /api/v1/dashboard`).
 *
 * Segue o mesmo guard de `useCurrentUser`: só executa depois que a store de
 * auth termina de reidratar e apenas quando há um `accessToken` — evita uma
 * chamada fadada a falhar logo no primeiro render.
 */
export function useDashboard() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: fetchDashboard,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
