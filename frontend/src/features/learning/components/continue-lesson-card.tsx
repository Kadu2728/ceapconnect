"use client";

import { ArrowRight, Clock, PlayCircle } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import type { LessonSummary } from "@/features/learning/types/learning.types";
import { formatDuration, formatTimestamp } from "@/features/learning/utils/video-source";

interface ContinueLessonCardProps {
  lesson: LessonSummary;
  lessonHref: (lessonId: string) => string;
  /** Variante compacta para a home do responsável (sem o título de seção). */
  compact?: boolean;
}

/**
 * "Continue sua formação" — a principal ação da página. Uma aula só, a que
 * vem a seguir: o princípio central do CEAP Connect (a pessoa sempre sabe
 * o próximo passo) aplicado à formação.
 */
export function ContinueLessonCard({
  lesson,
  lessonHref,
  compact = false,
}: ContinueLessonCardProps) {
  const isInProgress = lesson.status === "in_progress";

  return (
    <DashboardCard className="border-brand/25 bg-brand/[0.04]">
      {!compact ? (
        <p className="text-xs font-semibold uppercase tracking-wider text-brand">
          Continue sua formação
        </p>
      ) : (
        <p className="text-xs font-semibold uppercase tracking-wider text-brand">
          Sua formação
        </p>
      )}

      <h3 className="mt-2 text-lg font-semibold text-pretty">{lesson.title}</h3>

      <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
        <span className="inline-flex items-center gap-1.5">
          <PlayCircle className="size-4" aria-hidden="true" />
          Videoaula
        </span>
        <span className="inline-flex items-center gap-1.5">
          <Clock className="size-4" aria-hidden="true" />
          {formatDuration(lesson.duration_seconds)}
        </span>
        {isInProgress ? (
          <span className="font-medium text-foreground">
            Continuar de {formatTimestamp(lesson.resume_position_seconds)}
          </span>
        ) : null}
      </div>

      <Button asChild size="lg" className="mt-5 w-full gap-2 sm:w-fit">
        <Link href={lessonHref(lesson.id)}>
          {isInProgress ? "Continuar aula" : "Começar aula"}
          <ArrowRight className="size-4" aria-hidden="true" />
        </Link>
      </Button>
    </DashboardCard>
  );
}
