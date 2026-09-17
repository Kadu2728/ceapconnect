"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchCourseOverview } from "@/features/learning/services/learning.service";

export const COURSE_OVERVIEW_QUERY_KEY = (slug: string) =>
  ["learning", "course", slug] as const;

/**
 * Visão geral do curso (`GET /learning/courses/{slug}`) — a página inteira
 * da formação numa resposta leve, sem vídeo. Mesmo guard de sessão das
 * outras queries autenticadas.
 */
export function useCourseOverview(slug: string) {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: COURSE_OVERVIEW_QUERY_KEY(slug),
    queryFn: () => fetchCourseOverview(slug),
    enabled: hasHydrated && Boolean(accessToken) && Boolean(slug),
  });
}
