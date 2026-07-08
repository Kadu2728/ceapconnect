"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchAchievements } from "@/features/achievements/services/achievement.service";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const ACHIEVEMENTS_QUERY_KEY = ["achievements"] as const;

/**
 * Busca as conquistas do candidato (`GET /api/v1/achievements`). Mesmo guard de
 * sessão do Dashboard. A chave é reutilizada por `useCompleteMission` para
 * invalidar a lista quando uma conquista é desbloqueada.
 */
export function useAchievements() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: ACHIEVEMENTS_QUERY_KEY,
    queryFn: fetchAchievements,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
