"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { completeOnboarding } from "@/features/onboarding/services/onboarding.service";

/**
 * Marca o onboarding como concluído (`POST /api/v1/onboarding/complete`) e
 * invalida o dashboard para refletir `onboarded: true`.
 */
export function useCompleteOnboarding() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: completeOnboarding,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
  });
}
