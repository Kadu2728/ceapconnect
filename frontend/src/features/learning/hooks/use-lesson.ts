"use client";

import { useQuery } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { fetchLesson } from "@/features/learning/services/learning.service";

export const LESSON_QUERY_KEY = (lessonId: string) =>
  ["learning", "lesson", lessonId] as const;

/**
 * A aula para assistir (`GET /learning/lessons/{id}`) — a única query que
 * carrega a URL do vídeo, e só quando a pessoa abriu a aula.
 *
 * `retry: false`: um 403 (curso de outro público) ou 404 não melhora
 * tentando de novo, e cada retentativa numa conexão lenta é uma tela de
 * loading a mais.
 */
export function useLesson(lessonId: string) {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  return useQuery({
    queryKey: LESSON_QUERY_KEY(lessonId),
    queryFn: () => fetchLesson(lessonId),
    enabled: hasHydrated && Boolean(accessToken) && Boolean(lessonId),
    retry: false,
  });
}
