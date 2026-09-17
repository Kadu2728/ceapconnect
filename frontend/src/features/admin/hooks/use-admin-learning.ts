"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import {
  createCourse,
  createLesson,
  createModule,
  fetchAdminCourseDetail,
  fetchAdminCourses,
  updateCourse,
  updateLesson,
  updateModule,
} from "@/features/admin/services/admin-learning.service";
import type {
  AdminCourseInput,
  AdminLessonInput,
  AdminModuleInput,
} from "@/features/admin/types/admin-learning.types";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";

export const ADMIN_COURSES_QUERY_KEY = ["admin", "learning", "courses"] as const;
export const ADMIN_COURSE_DETAIL_QUERY_KEY = (courseId: string) =>
  ["admin", "learning", "course", courseId] as const;

export function useAdminCourses() {
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);
  return useQuery({
    queryKey: ADMIN_COURSES_QUERY_KEY,
    queryFn: fetchAdminCourses,
    enabled: hasHydrated && Boolean(accessToken),
  });
}

/** Árvore completa de um curso — só quando o admin expande para editar. */
export function useAdminCourseDetail(courseId: string | null) {
  return useQuery({
    queryKey: ADMIN_COURSE_DETAIL_QUERY_KEY(courseId ?? ""),
    queryFn: () => fetchAdminCourseDetail(courseId as string),
    enabled: courseId !== null,
  });
}

/**
 * Toda escrita invalida a lista de gestão, o detalhe do curso tocado e a
 * visão pública (`["learning"]`) — uma aula nova aparece para o responsável
 * sem ele precisar recarregar, mesma disciplina de `useSaveReward`.
 */
function useInvalidateLearning() {
  const queryClient = useQueryClient();
  return (courseId?: string) => {
    queryClient.invalidateQueries({ queryKey: ADMIN_COURSES_QUERY_KEY });
    if (courseId) {
      queryClient.invalidateQueries({
        queryKey: ADMIN_COURSE_DETAIL_QUERY_KEY(courseId),
      });
    }
    queryClient.invalidateQueries({ queryKey: ["learning"] });
  };
}

function onSaveError(what: string) {
  return (error: unknown) =>
    toast.error(`Não foi possível salvar ${what}`, {
      description: extractApiErrorMessage(error, "Confira os dados e tente novamente."),
    });
}

export function useSaveCourse() {
  const invalidate = useInvalidateLearning();
  return useMutation({
    mutationFn: ({ id, input }: { id?: string; input: AdminCourseInput }) =>
      id ? updateCourse(id, input) : createCourse(input),
    onSuccess: (course, { id }) => {
      invalidate(course.id);
      toast.success(id ? "Curso atualizado" : "Curso criado");
    },
    onError: onSaveError("o curso"),
  });
}

export function useSaveModule(courseId: string) {
  const invalidate = useInvalidateLearning();
  return useMutation({
    mutationFn: ({ id, input }: { id?: string; input: AdminModuleInput }) =>
      id ? updateModule(id, input) : createModule(courseId, input),
    onSuccess: (_module, { id }) => {
      invalidate(courseId);
      toast.success(id ? "Módulo atualizado" : "Módulo criado");
    },
    onError: onSaveError("o módulo"),
  });
}

export function useSaveLesson(courseId: string) {
  const invalidate = useInvalidateLearning();
  return useMutation({
    mutationFn: ({
      id,
      moduleId,
      input,
    }: {
      id?: string;
      moduleId: string;
      input: AdminLessonInput;
    }) => (id ? updateLesson(id, input) : createLesson(moduleId, input)),
    onSuccess: (_lesson, { id }) => {
      invalidate(courseId);
      toast.success(id ? "Aula atualizada" : "Aula criada");
    },
    onError: onSaveError("a aula"),
  });
}
