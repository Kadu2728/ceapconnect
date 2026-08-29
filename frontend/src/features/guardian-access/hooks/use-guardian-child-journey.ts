"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchGuardianChildJourney } from "@/features/guardian-access/services/guardian-access.service";

export const GUARDIAN_CHILD_JOURNEY_QUERY_KEY = (candidateProfileId: string) =>
  ["guardian-child-journey", candidateProfileId] as const;

export function useGuardianChildJourney(candidateProfileId: string) {
  return useQuery({
    queryKey: GUARDIAN_CHILD_JOURNEY_QUERY_KEY(candidateProfileId),
    queryFn: () => fetchGuardianChildJourney(candidateProfileId),
    enabled: Boolean(candidateProfileId),
  });
}
