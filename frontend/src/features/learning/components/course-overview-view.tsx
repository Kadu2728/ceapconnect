"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { ContinueLessonCard } from "@/features/learning/components/continue-lesson-card";
import { CourseProgressCard } from "@/features/learning/components/course-progress-card";
import { ModuleList } from "@/features/learning/components/module-list";
import type { LearningRoutes } from "@/features/learning/constants";
import { useCourseOverview } from "@/features/learning/hooks/use-course-overview";

interface CourseOverviewViewProps {
  /** Slug do curso a exibir. */
  slug: string;
  /** Para onde cada aula leva — muda por área, o conteúdo não. */
  routes: LearningRoutes;
  /** `false` enquanto o guard de sessão/papel da página ainda não liberou. */
  ready: boolean;
  /** Título curto do card "continue" (ex.: "Continue sua formação"). */
  continueEyebrow: string;
}

/**
 * O dashboard de um curso — progresso, "continue de onde parou" e módulos.
 *
 * Um único componente para os dois públicos: a página do responsável e a do
 * candidato só decidem a casca e o guard; o corpo é este. Leve por
 * construção: uma única query (`CourseOverview`) que **nunca** traz a URL de
 * um vídeo — o vídeo só entra na página da aula.
 */
export function CourseOverviewView({
  slug,
  routes,
  ready,
  continueEyebrow,
}: CourseOverviewViewProps) {
  const overviewQuery = useCourseOverview(slug);

  if (!ready || overviewQuery.isPending) {
    return <CardListSkeleton count={3} withSummary />;
  }

  if (!overviewQuery.isSuccess) {
    return (
      <QueryErrorState
        onRetry={() => overviewQuery.refetch()}
        title="Não foi possível carregar o conteúdo"
      />
    );
  }

  const overview = overviewQuery.data;
  const nextLessonId = overview.next_lesson?.id;
  const nextModuleId =
    overview.modules.find((m) => m.lessons.some((l) => l.id === nextLessonId))?.id ??
    null;

  return (
    <div className="flex flex-col gap-6">
      <CourseProgressCard
        progressPercent={overview.progress_percent}
        completedLessons={overview.completed_lessons}
        totalLessons={overview.total_lessons}
      />

      {overview.next_lesson ? (
        <ContinueLessonCard
          lesson={overview.next_lesson}
          lessonHref={routes.lesson}
          eyebrow={continueEyebrow}
        />
      ) : null}

      <section aria-labelledby="modulos-heading">
        <h2 id="modulos-heading" className="mb-3 text-base font-semibold">
          Módulos do curso
        </h2>
        <ModuleList
          modules={overview.modules}
          lessonHref={routes.lesson}
          defaultOpenModuleId={nextModuleId}
        />
      </section>
    </div>
  );
}
