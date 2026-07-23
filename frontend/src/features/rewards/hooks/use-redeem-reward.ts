"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { REWARDS_QUERY_KEY } from "@/features/rewards/hooks/use-rewards";
import { redeemReward } from "@/features/rewards/services/reward.service";

/**
 * Resgata uma recompensa (`POST /api/v1/rewards/{id}/redeem`).
 *
 * Ao resgatar, invalida a lista de recompensas e o dashboard (a "próxima
 * recompensa" em destaque pode mudar). O feedback é dado via toast — reforço
 * positivo que fecha o ciclo "conquistou → resgatou".
 */
export function useRedeemReward() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: redeemReward,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: REWARDS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });

      toast.success("Recompensa resgatada! 🎉", {
        description: `"${result.reward.title}" está a caminho. Nossa equipe vai te enviar os próximos passos.`,
      });
    },
    onError: (error) => {
      toast.error("Não foi possível resgatar a recompensa", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
