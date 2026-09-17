"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { GuardianShell } from "@/components/layout/guardian-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireGuardian } from "@/features/auth/hooks/use-require-guardian";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { ContinueLessonCard } from "@/features/learning/components/continue-lesson-card";
import { CourseProgressCard } from "@/features/learning/components/course-progress-card";
import { ModuleList } from "@/features/learning/components/module-list";
import {
  GUARDIAN_COURSE_SLUG,
  GUARDIAN_LEARNING_ROUTES,
} from "@/features/learning/constants";
import { useCourseOverview } from "@/features/learning/hooks/use-course-overview";

/**
 * Formação de Pais — dashboard do curso do responsável.
 *
 * Página leve por construção: uma única query (`CourseOverview`) que traz
 * progresso, próxima aula e módulos com estado — e **nunca** a URL de um
 * vídeo. O vídeo só entra na página da aula, quando a pessoa escolhe assistir.
 */
export default function FormacaoPage() {
  const isAuthorized = useRequireGuardian();
  const storedUser = useAuthStore((state) => state.user);
  const overviewQuery = useCourseOverview(GUARDIAN_COURSE_SLUG);

  const nextModuleId =
    overviewQuery.data?.modules.find((m) =>
      m.lessons.some((l) => l.id === overviewQuery.data?.next_lesson?.id),
    )?.id ?? null;

  return (
    <GuardianShell userName={storedUser?.name ?? "responsável"}>
      <PageHeader
        eyebrow="Área do responsável"
        title="Formação de Pais"
        description="Acompanhe sua formação, assista às aulas e avance pelas etapas do curso."
      />

      {!isAuthorized || overviewQuery.isPending ? (
        <CardListSkeleton count={3} withSummary />
      ) : overviewQuery.isSuccess ? (
        <div className="flex flex-col gap-6">
          <CourseProgressCard
            progressPercent={overviewQuery.data.progress_percent}
            completedLessons={overviewQuery.data.completed_lessons}
            totalLessons={overviewQuery.data.total_lessons}
          />

          {overviewQuery.data.next_lesson ? (
            <ContinueLessonCard
              lesson={overviewQuery.data.next_lesson}
              lessonHref={GUARDIAN_LEARNING_ROUTES.lesson}
            />
          ) : null}

          <section aria-labelledby="modulos-heading">
            <h2 id="modulos-heading" className="mb-3 text-base font-semibold">
              Módulos do curso
            </h2>
            <ModuleList
              modules={overviewQuery.data.modules}
              lessonHref={GUARDIAN_LEARNING_ROUTES.lesson}
              defaultOpenModuleId={nextModuleId}
            />
          </section>
        </div>
      ) : (
        <QueryErrorState
          onRetry={() => overviewQuery.refetch()}
          title="Não foi possível carregar o conteúdo"
        />
      )}
    </GuardianShell>
  );
}
