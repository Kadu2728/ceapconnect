"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchAdminOverview } from "@/features/admin/services/admin.service";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const ADMIN_OVERVIEW_QUERY_KEY = ["admin", "overview"] as const;

/**
 * Busca as métricas do painel administrativo (`GET /api/v1/admin/overview`).
 * Só executa quando a store reidratou, há token e o usuário é admin — evita
 * uma chamada que retornaria 403 para candidatos comuns.
 */
export function useAdminOverview() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);
  const isAdmin = useAuthStore((state) => state.user?.is_admin ?? false);

  return useQuery({
    queryKey: ADMIN_OVERVIEW_QUERY_KEY,
    queryFn: fetchAdminOverview,
    enabled: hasHydrated && Boolean(accessToken) && isAdmin,
  });
}
