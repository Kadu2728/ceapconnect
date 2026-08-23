"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { GUARDIANS_AT_RISK_QUERY_KEY } from "@/features/guardians/hooks/use-guardians-at-risk";
import { setCohortTrainingDate } from "@/features/guardians/services/guardian.service";

interface SetCohortTrainingDateInput {
  cohortId: string;
  guardianTrainingDate: string | null;
}

/** Define a data única da formação obrigatória de uma coorte (Área de Pais). */
export function useSetCohortTrainingDate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ cohortId, guardianTrainingDate }: SetCohortTrainingDateInput) =>
      setCohortTrainingDate(cohortId, guardianTrainingDate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GUARDIANS_AT_RISK_QUERY_KEY });
      toast.success("Data da formação atualizada");
    },
    onError: (error) => {
      toast.error("Não foi possível atualizar a data", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
