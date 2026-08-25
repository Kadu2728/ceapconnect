"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchCandidateState } from "@/features/journey-os/services/journey-os.service";

export const CANDIDATE_STATE_QUERY_KEY = ["candidate-state"] as const;

/**
 * Busca o estado computado da jornada (`GET /candidate-state`) — o
 * `momentum` que decide se o Modo Resgate entra em cena. Mesmo guard de
 * `useDashboard`: só executa depois da store de auth reidratar.
 */
export function useCandidateState() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: CANDIDATE_STATE_QUERY_KEY,
    queryFn: fetchCandidateState,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
