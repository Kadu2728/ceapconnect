"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchMissions } from "@/features/missions/services/mission.service";

export const MISSIONS_QUERY_KEY = ["missions"] as const;

/**
 * Busca as missões do candidato (`GET /api/v1/missions`). Segue o mesmo guard
 * de sessão do Dashboard: só executa após a store reidratar e havendo token.
 */
export function useMissions() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: MISSIONS_QUERY_KEY,
    queryFn: fetchMissions,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
