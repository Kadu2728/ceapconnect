"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { GUARDIAN_PORTAL_QUERY_KEY } from "@/features/guardian-portal/hooks/use-guardian-portal";
import { confirmGuardianTraining } from "@/features/guardian-portal/services/guardian-portal.service";

export function useConfirmGuardianTraining(token: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => confirmGuardianTraining(token),
    onSuccess: (data) => {
      queryClient.setQueryData(GUARDIAN_PORTAL_QUERY_KEY(token), data);
    },
  });
}
