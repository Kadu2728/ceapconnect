"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { CANDIDATE_STATE_QUERY_KEY } from "@/features/journey-os/hooks/use-candidate-state";
import { NEXT_BEST_ACTION_QUERY_KEY } from "@/features/journey-os/hooks/use-next-best-action";
import {
  resumePause,
  startPause,
} from "@/features/journey-os/services/journey-os.service";
import type {
  PauseResumeResult,
  PauseStartRequest,
  PauseState,
} from "@/features/journey-os/types/journey-os.types";

const START_ERROR_MESSAGE = "Não conseguimos registrar sua pausa agora. Tente de novo.";
const RESUME_ERROR_MESSAGE = "Não conseguimos retomar agora. Tente de novo.";

/**
 * Pausar e retomar mexem no mesmo estado que decide a experiência inteira do
 * Dashboard (`candidate-state`, NBA e o agregado do Dashboard) — invalidar os
 * três de uma vez garante que a tela reflita a decisão no mesmo instante, sem
 * um frame intermediário mostrando cobrança para quem acabou de pausar.
 */
function useInvalidateJourneyState() {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: CANDIDATE_STATE_QUERY_KEY });
    queryClient.invalidateQueries({ queryKey: NEXT_BEST_ACTION_QUERY_KEY });
    queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
  };
}

/** Declara uma pausa curta (`POST /candidate/pause`). */
export function useStartPause() {
  const invalidate = useInvalidateJourneyState();

  return useMutation<PauseState, Error, PauseStartRequest>({
    mutationFn: async (payload) => {
      try {
        return await startPause(payload);
      } catch (error) {
        // O backend recusa a pausa quando a prova está perto demais, com uma
        // mensagem própria e acolhedora — preservá-la importa mais que um
        // texto genérico (é a única explicação que o candidato vai ler).
        throw new Error(extractApiErrorMessage(error, START_ERROR_MESSAGE));
      }
    },
    onSuccess: () => {
      invalidate();
      toast.success("Guardamos seu lugar.", {
        description: "Estaremos aqui quando você voltar.",
      });
    },
    onError: (error) => {
      toast.error("Não foi possível pausar", { description: error.message });
    },
  });
}

/** Retomada de 1 toque (`POST /candidate/pause/resume`). */
export function useResumePause() {
  const invalidate = useInvalidateJourneyState();

  return useMutation<PauseResumeResult, Error, void>({
    mutationFn: async () => {
      try {
        return await resumePause();
      } catch (error) {
        throw new Error(extractApiErrorMessage(error, RESUME_ERROR_MESSAGE));
      }
    },
    onSuccess: () => {
      invalidate();
    },
    onError: (error) => {
      toast.error("Não foi possível retomar", { description: error.message });
    },
  });
}
