"use client";

import { ArrowLeft, ArrowRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";

import { QueryErrorState } from "@/components/feedback/query-error-state";
import { Button } from "@/components/ui/button";
import { LessonPlayer } from "@/features/learning/components/lesson-player";
import type { LearningRoutes } from "@/features/learning/constants";
import { useLesson } from "@/features/learning/hooks/use-lesson";
import { useLessonProgress } from "@/features/learning/hooks/use-lesson-progress";
import { formatDuration } from "@/features/learning/utils/video-source";

interface LessonViewProps {
  lessonId: string;
  routes: LearningRoutes;
  /** `false` enquanto o guard de sessão/papel da página ainda não liberou. */
  ready: boolean;
  /** Rótulo do link de volta ao curso (ex.: "Formação de Pais"). */
  courseLabel: string;
}

/**
 * A aula — única tela que carrega vídeo, e só depois que a pessoa escolheu
 * assistir. Um `<video>` montado por vez; ao sair, o buffer é liberado (ver
 * `LessonPlayer`). Compartilhada pelos dois públicos: player, progresso e
 * navegação entre aulas são idênticos; só a casca e as rotas mudam.
 */
export function LessonView({ lessonId, routes, ready, courseLabel }: LessonViewProps) {
  const lessonQuery = useLesson(lessonId);
  const progress = useLessonProgress(lessonId, lessonQuery.data?.course_slug ?? "");

  return (
    <>
      <Link
        href={routes.course}
        className="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        {courseLabel}
      </Link>

      {!ready || lessonQuery.isPending ? (
        <div className="flex flex-col gap-4">
          <div className="aspect-video w-full animate-pulse rounded-2xl bg-muted" />
          <div className="h-6 w-2/3 animate-pulse rounded bg-muted" />
          <div className="h-4 w-1/3 animate-pulse rounded bg-muted" />
        </div>
      ) : lessonQuery.isSuccess ? (
        <div className="flex flex-col gap-6">
          <LessonPlayer
            provider={lessonQuery.data.video_provider}
            videoRef={lessonQuery.data.video_ref}
            title={lessonQuery.data.title}
            resumeFromSeconds={lessonQuery.data.resume_position_seconds}
            onTimeUpdate={progress.report}
            onPause={progress.flush}
            onEnded={progress.flush}
          />

          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {lessonQuery.data.module_title}
            </p>
            <h1 className="mt-1 text-xl font-semibold text-pretty sm:text-2xl">
              {lessonQuery.data.title}
            </h1>
            <p className="mt-1 flex flex-wrap items-center gap-x-3 text-sm text-muted-foreground">
              <span>{formatDuration(lessonQuery.data.duration_seconds)}</span>
              {lessonQuery.data.status === "completed" ? (
                <span className="inline-flex items-center gap-1 text-success">
                  <CheckCircle2 className="size-4" aria-hidden="true" />
                  Concluída
                </span>
              ) : null}
            </p>
            {lessonQuery.data.description ? (
              <p className="mt-3 max-w-prose text-pretty text-muted-foreground">
                {lessonQuery.data.description}
              </p>
            ) : null}
          </div>

          <nav aria-label="Navegar entre aulas" className="flex flex-wrap gap-3">
            {lessonQuery.data.previous_lesson_id ? (
              <Button asChild variant="outline" className="gap-2">
                <Link href={routes.lesson(lessonQuery.data.previous_lesson_id)}>
                  <ArrowLeft className="size-4" aria-hidden="true" />
                  Aula anterior
                </Link>
              </Button>
            ) : null}
            {lessonQuery.data.next_lesson_id ? (
              <Button asChild className="gap-2">
                <Link href={routes.lesson(lessonQuery.data.next_lesson_id)}>
                  Próxima aula
                  <ArrowRight className="size-4" aria-hidden="true" />
                </Link>
              </Button>
            ) : (
              <Button asChild variant="outline">
                <Link href={routes.course}>Voltar para o curso</Link>
              </Button>
            )}
          </nav>
        </div>
      ) : (
        <QueryErrorState
          onRetry={() => lessonQuery.refetch()}
          title="Não foi possível carregar esta aula"
          description="Verifique sua conexão e tente novamente. Se o problema continuar, volte ao curso."
        />
      )}
    </>
  );
}
