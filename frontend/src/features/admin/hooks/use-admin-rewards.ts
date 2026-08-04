"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchAdminRewards } from "@/features/admin/services/admin.service";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const ADMIN_REWARDS_QUERY_KEY = ["admin", "rewards"] as const;

/**
 * Busca o catálogo de gestão de recompensas (`GET /api/v1/admin/rewards`).
 * Mesmo guard de admin do overview: só executa para admins autenticados.
 */
export function useAdminRewards() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);
  const isAdmin = useAuthStore((state) => state.user?.is_admin ?? false);

  return useQuery({
    queryKey: ADMIN_REWARDS_QUERY_KEY,
    queryFn: fetchAdminRewards,
    enabled: hasHydrated && Boolean(accessToken) && isAdmin,
  });
}
