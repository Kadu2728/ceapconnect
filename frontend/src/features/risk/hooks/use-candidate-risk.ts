"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchCandidateRisk } from "@/features/risk/services/risk.service";

export const CANDIDATE_RISK_QUERY_KEY = ["risk", "candidate"] as const;

/**
 * Busca o detalhe de risco de um candidato (`GET /admin/candidates/{id}/risk`).
 * `candidateProfileId === null` desabilita a query — usado quando a gaveta de
 * intervenção está fechada (nenhum candidato selecionado).
 */
export function useCandidateRisk(candidateProfileId: string | null) {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: [...CANDIDATE_RISK_QUERY_KEY, candidateProfileId],
    queryFn: () => fetchCandidateRisk(candidateProfileId as string),
    enabled: hasHydrated && Boolean(accessToken) && candidateProfileId !== null,
  });
}
