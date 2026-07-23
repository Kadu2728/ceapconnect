"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchRedemptions } from "@/features/admin/services/admin.service";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const ADMIN_REDEMPTIONS_QUERY_KEY = ["admin", "redemptions"] as const;

/**
 * Busca a fila de resgates de recompensas (`GET /api/v1/admin/redemptions`).
 * Mesmo guard de admin do overview: só executa para admins autenticados.
 */
export function useRedemptions() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);
  const isAdmin = useAuthStore((state) => state.user?.is_admin ?? false);

  return useQuery({
    queryKey: ADMIN_REDEMPTIONS_QUERY_KEY,
    queryFn: fetchRedemptions,
    enabled: hasHydrated && Boolean(accessToken) && isAdmin,
  });
}
