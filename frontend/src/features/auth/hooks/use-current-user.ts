"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchCurrentUser } from "@/features/auth/services/auth.service";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const CURRENT_USER_QUERY_KEY = ["auth", "me"] as const;

/**
 * Busca o perfil do usuário autenticado (`GET /users/me`).
 *
 * Serve como a confirmação de ponta a ponta de que o token guardado na
 * store realmente funciona contra o backend — a store por si só só garante
 * que *algum* token existe, não que ele é válido.
 *
 * Só executa depois que a store termina de reidratar (`hasHydrated`) e
 * apenas quando há um `accessToken`, evitando uma chamada fadada a falhar
 * logo no primeiro render.
 */
export function useCurrentUser() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: CURRENT_USER_QUERY_KEY,
    queryFn: fetchCurrentUser,
    enabled: hasHydrated && Boolean(accessToken),
  });
}
