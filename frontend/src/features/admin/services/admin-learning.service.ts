import { apiClient } from "@/lib/axios";

import type {
  AdminCourse,
  AdminCourseDetail,
  AdminCourseInput,
  AdminCourseList,
  AdminLesson,
  AdminLessonInput,
  AdminModule,
  AdminModuleInput,
} from "@/features/admin/types/admin-learning.types";
import type { ApiEnvelope } from "@/types/api";

/** Service da gestão de cursos — única camada que fala com `apiClient` aqui. */
const ENDPOINT = "/api/v1/admin/learning";

export async function fetchAdminCourses(): Promise<AdminCourseList> {
  const { data } = await apiClient.get<ApiEnvelope<AdminCourseList>>(
    `${ENDPOINT}/courses`,
  );
  return data.data;
}

export async function fetchAdminCourseDetail(
  courseId: string,
): Promise<AdminCourseDetail> {
  const { data } = await apiClient.get<ApiEnvelope<AdminCourseDetail>>(
    `${ENDPOINT}/courses/${courseId}`,
  );
  return data.data;
}

export async function createCourse(input: AdminCourseInput): Promise<AdminCourse> {
  const { data } = await apiClient.post<ApiEnvelope<AdminCourse>>(
    `${ENDPOINT}/courses`,
    input,
  );
  return data.data;
}

export async function updateCourse(
  courseId: string,
  input: AdminCourseInput,
): Promise<AdminCourse> {
  const { data } = await apiClient.patch<ApiEnvelope<AdminCourse>>(
    `${ENDPOINT}/courses/${courseId}`,
    input,
  );
  return data.data;
}

export async function createModule(
  courseId: string,
  input: AdminModuleInput,
): Promise<AdminModule> {
  const { data } = await apiClient.post<ApiEnvelope<AdminModule>>(
    `${ENDPOINT}/courses/${courseId}/modules`,
    input,
  );
  return data.data;
}

export async function updateModule(
  moduleId: string,
  input: AdminModuleInput,
): Promise<AdminModule> {
  const { data } = await apiClient.patch<ApiEnvelope<AdminModule>>(
    `${ENDPOINT}/modules/${moduleId}`,
    input,
  );
  return data.data;
}

export async function createLesson(
  moduleId: string,
  input: AdminLessonInput,
): Promise<AdminLesson> {
  const { data } = await apiClient.post<ApiEnvelope<AdminLesson>>(
    `${ENDPOINT}/modules/${moduleId}/lessons`,
    input,
  );
  return data.data;
}

export async function updateLesson(
  lessonId: string,
  input: AdminLessonInput,
): Promise<AdminLesson> {
  const { data } = await apiClient.patch<ApiEnvelope<AdminLesson>>(
    `${ENDPOINT}/lessons/${lessonId}`,
    input,
  );
  return data.data;
}
