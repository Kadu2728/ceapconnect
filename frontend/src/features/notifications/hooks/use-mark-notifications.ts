"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { DASHBOARD_QUERY_KEY } from "@/features/dashboard/hooks/use-dashboard";
import { NOTIFICATIONS_QUERY_KEY } from "@/features/notifications/hooks/use-notifications";
import {
  markAllNotificationsRead,
  markNotificationRead,
} from "@/features/notifications/services/notification.service";

/** Invalida a lista e o dashboard (o contador do sino vem do dashboard). */
function invalidateNotificationViews(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: NOTIFICATIONS_QUERY_KEY });
  queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY });
}

/** Marca uma notificação como lida (`POST /notifications/{id}/read`). */
export function useMarkNotificationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => invalidateNotificationViews(queryClient),
  });
}

/** Marca todas as notificações como lidas (`POST /notifications/read-all`). */
export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: (result) => {
      invalidateNotificationViews(queryClient);
      if (result.marked > 0) {
        toast.success("Notificações marcadas como lidas");
      }
    },
    onError: (error) => {
      toast.error("Não foi possível marcar como lidas", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
