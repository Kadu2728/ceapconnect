"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchNextBestAction } from "@/features/journey-os/services/journey-os.service";

export const NEXT_BEST_ACTION_QUERY_KEY = ["next-best-action"] as const;

/** Busca a recomendação única do candidato (`GET /next-best-action`), ou `null`. */
export function useNextBestAction() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: NEXT_BEST_ACTION_QUERY_KEY,
    queryFn: fetchNextBestAction,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
