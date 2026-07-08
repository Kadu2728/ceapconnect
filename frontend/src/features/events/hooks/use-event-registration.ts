"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { EVENTS_QUERY_KEY } from "@/features/events/hooks/use-events";
import {
  cancelEventRegistration,
  registerEvent,
} from "@/features/events/services/event.service";

interface ToggleRegistrationInput {
  eventId: string;
  /** Estado atual da inscrição — decide entre inscrever e cancelar. */
  registered: boolean;
}

/**
 * Inscreve ou cancela a inscrição em um evento (`POST`/`DELETE
 * /api/v1/events/{id}/register`), conforme o estado atual. Invalida eventos e
 * dashboard (a inscrição gera notificação, alterando o contador do sino).
 */
export function useEventRegistration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ eventId, registered }: ToggleRegistrationInput) =>
      registered ? cancelEventRegistration(eventId) : registerEvent(eventId),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: EVENTS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });

      if (result.registered) {
        toast.success("Inscrição confirmada!", {
          description: `Você está inscrito em "${result.event.title}".`,
        });
      } else {
        toast.success("Inscrição cancelada", {
          description: `Você saiu de "${result.event.title}".`,
        });
      }
    },
    onError: (error) => {
      toast.error("Não foi possível atualizar sua inscrição", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
