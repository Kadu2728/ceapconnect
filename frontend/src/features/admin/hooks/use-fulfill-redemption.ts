"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { ADMIN_REDEMPTIONS_QUERY_KEY } from "@/features/admin/hooks/use-redemptions";
import { fulfillRedemption } from "@/features/admin/services/admin.service";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";

/**
 * Confirma a entrega de um resgate (`POST /admin/redemptions/{id}/fulfill`).
 * Invalida a fila de resgates; o aluno recebe uma notificação real do backend.
 */
export function useFulfillRedemption() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: fulfillRedemption,
    onSuccess: (redemption) => {
      queryClient.invalidateQueries({ queryKey: ADMIN_REDEMPTIONS_QUERY_KEY });
      toast.success("Entrega confirmada", {
        description: `${redemption.student_name} foi notificado sobre "${redemption.reward_title}".`,
      });
    },
    onError: (error) => {
      toast.error("Não foi possível confirmar a entrega", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
