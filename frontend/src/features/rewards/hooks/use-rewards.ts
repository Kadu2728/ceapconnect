"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchRewards } from "@/features/rewards/services/reward.service";

export const REWARDS_QUERY_KEY = ["rewards"] as const;

/**
 * Busca as recompensas do candidato (`GET /api/v1/rewards`). Mesmo guard de
 * sessão do Dashboard: só executa após a store reidratar e havendo token. A
 * chave é reutilizada por `useRedeemReward` para invalidar a lista no resgate.
 */
export function useRewards() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: REWARDS_QUERY_KEY,
    queryFn: fetchRewards,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
