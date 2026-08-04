"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { ADMIN_REWARDS_QUERY_KEY } from "@/features/admin/hooks/use-admin-rewards";
import { createReward, updateReward } from "@/features/admin/services/admin.service";
import type { AdminRewardInput } from "@/features/admin/types/admin.types";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";

interface SaveRewardArgs {
  /** Quando presente, edita a recompensa; ausente, cria uma nova. */
  id?: string;
  input: AdminRewardInput;
}

/**
 * Cria ou edita uma recompensa (`POST`/`PATCH /admin/rewards`). Invalida a lista
 * de gestão e também a vitrine do candidato (`rewards`) — mudanças no catálogo
 * refletem imediatamente para os alunos.
 */
export function useSaveReward() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, input }: SaveRewardArgs) =>
      id ? updateReward(id, input) : createReward(input),
    onSuccess: (_reward, { id }) => {
      queryClient.invalidateQueries({ queryKey: ADMIN_REWARDS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["rewards"] });
      toast.success(id ? "Recompensa atualizada" : "Recompensa criada");
    },
    onError: (error) => {
      toast.error("Não foi possível salvar a recompensa", {
        description: extractApiErrorMessage(error, "Confira os dados e tente novamente."),
      });
    },
  });
}
