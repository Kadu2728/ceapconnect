"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchGuardianLinks } from "@/features/profile/services/profile.service";

export const GUARDIAN_LINKS_QUERY_KEY = ["profile", "guardian-links"] as const;

/** Responsáveis que pediram vínculo com a conta (RBAC do responsável — fase C). */
export function useGuardianLinks() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: GUARDIAN_LINKS_QUERY_KEY,
    queryFn: fetchGuardianLinks,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
