import { apiClient } from "@/lib/axios";

import type {
  CourseCard,
  CourseOverview,
  LessonDetail,
  ProgressUpdateResult,
} from "@/features/learning/types/learning.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service do módulo de Videoaulas — única camada autorizada a falar com
 * `apiClient` neste domínio. Qual conteúdo cada papel vê é decidido no
 * backend pelo público do curso; aqui só há transporte.
 */
const LEARNING_ENDPOINT = "/api/v1/learning";

export async function fetchCourses(): Promise<CourseCard[]> {
  const { data } = await apiClient.get<ApiEnvelope<CourseCard[]>>(
    `${LEARNING_ENDPOINT}/courses`,
  );
  return data.data;
}

export async function fetchCourseOverview(slug: string): Promise<CourseOverview> {
  const { data } = await apiClient.get<ApiEnvelope<CourseOverview>>(
    `${LEARNING_ENDPOINT}/courses/${slug}`,
  );
  return data.data;
}

export async function fetchLesson(lessonId: string): Promise<LessonDetail> {
  const { data } = await apiClient.get<ApiEnvelope<LessonDetail>>(
    `${LEARNING_ENDPOINT}/lessons/${lessonId}`,
  );
  return data.data;
}

export async function updateLessonProgress(
  lessonId: string,
  positionSeconds: number,
): Promise<ProgressUpdateResult> {
  const { data } = await apiClient.put<ApiEnvelope<ProgressUpdateResult>>(
    `${LEARNING_ENDPOINT}/lessons/${lessonId}/progress`,
    { position_seconds: positionSeconds },
  );
  return data.data;
}
