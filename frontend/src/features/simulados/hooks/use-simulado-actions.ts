"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { SIMULADO_HISTORY_QUERY_KEY } from "@/features/simulados/hooks/use-simulado-history";
import {
  answerQuestion,
  finishSimulado,
  startSimulado,
} from "@/features/simulados/services/simulado.service";

/** Inicia um novo simulado (`POST /simulados/start`). */
export function useStartSimulado() {
  return useMutation({
    mutationFn: startSimulado,
    onError: (error) => {
      toast.error("Não foi possível iniciar o simulado", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}

/** Responde uma questão (`POST /simulados/{id}/answer`) — feedback imediato. */
export function useAnswerQuestion() {
  return useMutation({
    mutationFn: ({
      attemptId,
      questionId,
      selectedOptionKey,
    }: {
      attemptId: string;
      questionId: string;
      selectedOptionKey: string;
    }) => answerQuestion(attemptId, questionId, selectedOptionKey),
    onError: (error) => {
      toast.error("Não foi possível registrar a resposta", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}

/**
 * Finaliza o simulado (`POST /simulados/{id}/finish`). Invalida histórico e
 * dashboard — o simulado concede XP, então o nível exibido pode mudar.
 */
export function useFinishSimulado() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: finishSimulado,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SIMULADO_HISTORY_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
    },
    onError: (error) => {
      toast.error("Não foi possível finalizar o simulado", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
