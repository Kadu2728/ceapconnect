"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { ACHIEVEMENTS_QUERY_KEY } from "@/features/achievements/hooks/use-achievements";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { PROFILE_QUERY_KEY } from "@/features/profile/hooks/use-profile";
import { updateProfile } from "@/features/profile/services/profile.service";
import { REWARDS_QUERY_KEY } from "@/features/rewards/hooks/use-rewards";

/**
 * Atualiza o perfil (`PATCH /api/v1/profile`).
 *
 * Sincroniza o nome na store de sessão (usado pela navbar) e invalida perfil,
 * dashboard, conquistas e recompensas — salvar o perfil pode desbloquear a
 * conquista "Perfil Completo" (e, por consequência, recompensas).
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateProfile,
    onSuccess: (profile) => {
      const { accessToken, refreshToken, user } = useAuthStore.getState();
      if (accessToken && refreshToken && user && user.name !== profile.name) {
        useAuthStore.getState().setSession({
          accessToken,
          refreshToken,
          user: { ...user, name: profile.name },
        });
      }

      queryClient.invalidateQueries({ queryKey: PROFILE_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ACHIEVEMENTS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: REWARDS_QUERY_KEY });

      toast.success("Perfil atualizado com sucesso!");
    },
    onError: (error) => {
      toast.error("Não foi possível salvar o perfil", {
        description: extractApiErrorMessage(error, "Confira os dados e tente novamente."),
      });
    },
  });
}
