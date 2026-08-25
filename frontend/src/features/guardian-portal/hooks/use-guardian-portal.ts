"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchGuardianPortal } from "@/features/guardian-portal/services/guardian-portal.service";

export const GUARDIAN_PORTAL_QUERY_KEY = (token: string) =>
  ["guardian-portal", token] as const;

/**
 * Busca os dados do link mágico do responsável. Sem guard de sessão (a
 * própria rota é pública) — só precisa de um `token` não vazio.
 */
export function useGuardianPortal(token: string) {
  return useQuery({
    queryKey: GUARDIAN_PORTAL_QUERY_KEY(token),
    queryFn: () => fetchGuardianPortal(token),
    enabled: Boolean(token),
    retry: false,
  });
}
