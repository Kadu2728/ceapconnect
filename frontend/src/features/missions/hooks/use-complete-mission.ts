"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { ACHIEVEMENTS_QUERY_KEY } from "@/features/achievements/hooks/use-achievements";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { MISSIONS_QUERY_KEY } from "@/features/missions/hooks/use-missions";
import { completeMission } from "@/features/missions/services/mission.service";

/**
 * Conclui uma missão (`POST /api/v1/missions/{id}/complete`).
 *
 * Ao concluir, invalida missões, dashboard e conquistas (o XP e possíveis
 * conquistas mudam de uma vez). O feedback de XP/conquista é dado via toast —
 * fecha o ciclo de "ação → recompensa" do USER_FLOW com reforço positivo.
 */
export function useCompleteMission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: completeMission,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: MISSIONS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ACHIEVEMENTS_QUERY_KEY });

      const unlocked = result.unlocked_achievements;
      toast.success(`+${result.xp_gained} XP conquistados!`, {
        description:
          unlocked.length > 0
            ? `Nova conquista: ${unlocked.map((achievement) => achievement.name).join(", ")}`
            : "Missão concluída. Continue avançando na sua jornada.",
      });
    },
    onError: (error) => {
      toast.error("Não foi possível concluir a missão", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
