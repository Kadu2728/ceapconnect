"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { PROFILE_QUERY_KEY } from "@/features/profile/hooks/use-profile";
import { notifyGuardianTrainingByEmail } from "@/features/profile/services/profile.service";

/**
 * Envia o e-mail de aviso da formação obrigatória ao responsável, com o
 * link de confirmação (`POST /api/v1/profile/guardian/notify-training`).
 *
 * Mesmo contrato de `useNotifyGuardianEmail`: sempre 200, resultado real em
 * `result.sent`.
 */
export function useNotifyGuardianTrainingEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: notifyGuardianTrainingByEmail,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: PROFILE_QUERY_KEY });
      if (result.sent) {
        toast.success("Aviso enviado!", { description: result.message });
      } else {
        toast.error("Não foi possível enviar agora", { description: result.message });
      }
    },
    onError: (error) => {
      toast.error("Não foi possível enviar o aviso", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
