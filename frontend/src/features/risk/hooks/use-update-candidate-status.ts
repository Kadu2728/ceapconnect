"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { CANDIDATE_RISK_QUERY_KEY } from "@/features/risk/hooks/use-candidate-risk";
import { RISK_QUEUE_QUERY_KEY } from "@/features/risk/hooks/use-risk-queue";
import { updateCandidateStatus } from "@/features/risk/services/risk.service";

/**
 * Registra o outcome real do candidato (`PATCH /admin/candidates/{id}/status`)
 * — o rótulo manual que vai sustentar o harness de backtest do modelo de
 * risco. Invalida a fila (o candidato sai dela imediatamente, sem esperar o
 * próximo recálculo) e o detalhe exibido na gaveta.
 */
export function useUpdateCandidateStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateCandidateStatus,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RISK_QUEUE_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: CANDIDATE_RISK_QUERY_KEY });
      toast.success("Status atualizado");
    },
    onError: (error) => {
      toast.error("Não foi possível atualizar o status", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
