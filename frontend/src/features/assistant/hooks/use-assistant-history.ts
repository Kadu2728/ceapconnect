"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchAssistantHistory } from "@/features/assistant/services/assistant.service";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const ASSISTANT_HISTORY_QUERY_KEY = ["assistant", "history"] as const;

/**
 * Carrega o histórico de conversa com o assistente. `enabled` permite só
 * buscar quando o widget é aberto (evita uma chamada em toda página).
 */
export function useAssistantHistory(enabled: boolean) {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: ASSISTANT_HISTORY_QUERY_KEY,
    queryFn: fetchAssistantHistory,
    enabled: enabled && hasHydrated && Boolean(accessToken),
    staleTime: 60_000,
  });
}
