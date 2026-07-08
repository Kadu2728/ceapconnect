import { QueryClient } from "@tanstack/react-query";

/**
 * Fábrica do TanStack Query Client.
 *
 * `staleTime` conservador evita refetch agressivo em uma plataforma usada
 * majoritariamente em mobile pelo público de 16–25 anos, poupando dados
 * móveis do candidato. Uma fábrica (em vez de singleton no módulo) é usada
 * para garantir uma instância por request no SSR, evitando vazamento de
 * cache entre usuários.
 */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: 0,
      },
    },
  });
}
