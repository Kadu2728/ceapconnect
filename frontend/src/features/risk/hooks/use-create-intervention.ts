"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { CANDIDATE_RISK_QUERY_KEY } from "@/features/risk/hooks/use-candidate-risk";
import { RISK_QUEUE_QUERY_KEY } from "@/features/risk/hooks/use-risk-queue";
import { createIntervention } from "@/features/risk/services/risk.service";

/**
 * Registra uma intervenção (`POST /admin/interventions`). Invalida a fila e o
 * detalhe do candidato — o histórico de intervenções aparece na hora na
 * gaveta, sem precisar reabrir.
 */
export function useCreateIntervention() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createIntervention,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RISK_QUEUE_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: CANDIDATE_RISK_QUERY_KEY });
      toast.success("Intervenção registrada", {
        description: "O resultado será medido automaticamente em 7 dias.",
      });
    },
    onError: (error) => {
      toast.error("Não foi possível registrar a intervenção", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
