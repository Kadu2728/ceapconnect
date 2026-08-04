"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchNotifications } from "@/features/notifications/services/notification.service";

export const NOTIFICATIONS_QUERY_KEY = ["notifications"] as const;

/**
 * Busca as notificações do candidato (`GET /api/v1/notifications`). Mesmo guard
 * de sessão do Dashboard. A chave é reutilizada pelas mutations de "marcar como
 * lida" para invalidar a lista.
 */
export function useNotifications() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: NOTIFICATIONS_QUERY_KEY,
    queryFn: fetchNotifications,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
