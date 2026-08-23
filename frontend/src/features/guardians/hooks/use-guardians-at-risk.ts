"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchGuardiansAtRisk } from "@/features/guardians/services/guardian.service";

export const GUARDIANS_AT_RISK_QUERY_KEY = ["guardians", "at-risk"] as const;

/**
 * Busca as famílias que precisam de atenção (`GET /admin/guardians/at-risk`).
 * Mesmo guard de `useRiskQueue`: só roda pra coordenador/admin já hidratado.
 */
export function useGuardiansAtRisk() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);
  const isAdmin = useAuthStore((state) => state.user?.is_admin ?? false);
  const role = useAuthStore((state) => state.user?.role ?? "candidate");
  const isStaff = isAdmin || role === "coordinator";

  return useQuery({
    queryKey: GUARDIANS_AT_RISK_QUERY_KEY,
    queryFn: fetchGuardiansAtRisk,
    enabled: hasHydrated && Boolean(accessToken) && isStaff,
  });
}
