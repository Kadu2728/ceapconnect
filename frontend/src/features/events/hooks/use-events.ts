"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchEvents } from "@/features/events/services/event.service";

export const EVENTS_QUERY_KEY = ["events"] as const;

/**
 * Busca os próximos eventos com o status de inscrição do candidato
 * (`GET /api/v1/events`). Mesmo guard de sessão do Dashboard.
 */
export function useEvents() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: EVENTS_QUERY_KEY,
    queryFn: fetchEvents,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
