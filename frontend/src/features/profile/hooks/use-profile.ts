"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchProfile } from "@/features/profile/services/profile.service";

export const PROFILE_QUERY_KEY = ["profile"] as const;

/**
 * Busca o perfil do candidato (`GET /api/v1/profile`). Mesmo guard de sessão do
 * Dashboard: só executa após a store reidratar e havendo token.
 */
export function useProfile() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: PROFILE_QUERY_KEY,
    queryFn: fetchProfile,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
