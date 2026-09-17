"use client";

import { CheckCircle2, Clock, PlayCircle } from "lucide-react";
import Link from "next/link";

import type {
  LessonStatus,
  LessonSummary,
} from "@/features/learning/types/learning.types";
import { formatDuration, formatTimestamp } from "@/features/learning/utils/video-source";
import { cn } from "@/lib/utils";

interface LessonRowProps {
  lesson: LessonSummary;
  href: string;
}

/**
 * Estado de cada aula, legível de relance — e nunca só por cor (WCAG 1.4.1):
 * ícone + rótulo em texto para cada estado.
 */
const STATUS_PRESENTATION: Record<
  LessonStatus,
  { label: string; action: string; icon: typeof PlayCircle; className: string }
> = {
  available: {
    label: "Disponível",
    action: "Assistir",
    icon: PlayCircle,
    className: "text-muted-foreground",
  },
  in_progress: {
    label: "Em andamento",
    action: "Continuar",
    icon: PlayCircle,
    className: "text-warning",
  },
  completed: {
    label: "Concluída",
    action: "Rever",
    icon: CheckCircle2,
    className: "text-success",
  },
};

export function LessonRow({ lesson, href }: LessonRowProps) {
  const presentation = STATUS_PRESENTATION[lesson.status];
  const Icon = presentation.icon;
  const isInProgress = lesson.status === "in_progress";

  return (
    <Link
      href={href}
      className="flex items-center gap-3 rounded-xl px-3 py-3 transition-colors hover:bg-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <Icon
        className={cn("size-5 shrink-0", presentation.className)}
        aria-hidden="true"
      />

      <div className="min-w-0 flex-1">
        <p
          className={cn(
            "text-sm",
            lesson.status === "completed" ? "text-muted-foreground" : "font-medium",
          )}
        >
          {lesson.title}
        </p>
        <p className="mt-0.5 flex flex-wrap items-center gap-x-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <Clock className="size-3" aria-hidden="true" />
            {formatDuration(lesson.duration_seconds)}
          </span>
          <span className={presentation.className}>{presentation.label}</span>
          {isInProgress ? (
            <span>Continuar de {formatTimestamp(lesson.resume_position_seconds)}</span>
          ) : null}
        </p>
        {isInProgress ? (
          <div
            role="progressbar"
            aria-valuenow={lesson.watched_percent}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`${lesson.watched_percent}% assistido`}
            className="mt-2 h-1 w-full max-w-xs overflow-hidden rounded-full bg-muted"
          >
            <div
              className="h-full bg-warning"
              style={{ width: `${lesson.watched_percent}%` }}
            />
          </div>
        ) : null}
      </div>

      <span className="shrink-0 text-xs font-medium text-primary">
        {presentation.action}
      </span>
    </Link>
  );
}
