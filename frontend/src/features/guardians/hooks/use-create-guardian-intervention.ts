"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { GUARDIANS_AT_RISK_QUERY_KEY } from "@/features/guardians/hooks/use-guardians-at-risk";
import { createGuardianIntervention } from "@/features/guardians/services/guardian.service";

/**
 * Registra uma intervenção com o responsável (`POST /admin/guardians/interventions`).
 */
export function useCreateGuardianIntervention() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createGuardianIntervention,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GUARDIANS_AT_RISK_QUERY_KEY });
      toast.success("Contato registrado");
    },
    onError: (error) => {
      toast.error("Não foi possível registrar o contato", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
