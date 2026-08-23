"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { GUARDIANS_AT_RISK_QUERY_KEY } from "@/features/guardians/hooks/use-guardians-at-risk";
import {
  markTrainingAttended,
  markTrainingConfirmed,
} from "@/features/guardians/services/guardian.service";
import { RISK_QUEUE_QUERY_KEY } from "@/features/risk/hooks/use-risk-queue";

/** Marca que o responsável confirmou presença — sinal leve, não fecha o caso. */
export function useMarkTrainingConfirmed() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: markTrainingConfirmed,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GUARDIANS_AT_RISK_QUERY_KEY });
      toast.success("Confirmação registrada");
    },
    onError: (error) => {
      toast.error("Não foi possível registrar a confirmação", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}

/**
 * Marca presença de fato na formação — some da lista de risco, zera o sinal
 * de risco do responsável e desbloqueia o marco na jornada do candidato.
 * Invalida também a fila de risco de candidatos: o score deles muda junto.
 */
export function useMarkTrainingAttended() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: markTrainingAttended,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GUARDIANS_AT_RISK_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: RISK_QUEUE_QUERY_KEY });
      toast.success("Presença registrada", {
        description: "O responsável saiu da lista de risco.",
      });
    },
    onError: (error) => {
      toast.error("Não foi possível registrar a presença", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
