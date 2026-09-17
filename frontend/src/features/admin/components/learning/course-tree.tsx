"use client";

import { EyeOff, Pencil, Plus } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { LessonForm } from "@/features/admin/components/learning/lesson-form";
import { ModuleForm } from "@/features/admin/components/learning/module-form";
import { useAdminCourseDetail } from "@/features/admin/hooks/use-admin-learning";
import type {
  AdminLesson,
  AdminModule,
} from "@/features/admin/types/admin-learning.types";
import type { VideoProvider } from "@/features/learning/types/learning.types";
import { formatDuration } from "@/features/learning/utils/video-source";
import { cn } from "@/lib/utils";

interface CourseTreeProps {
  courseId: string;
  providers: VideoProvider[];
  completionThreshold: number;
}

/** O que está sendo editado: um formulário aberto por vez, para a tela não virar um mural. */
type Editing =
  | { kind: "module"; module?: AdminModule }
  | { kind: "lesson"; moduleId: string; lesson?: AdminLesson }
  | null;

/**
 * Módulos e aulas de um curso, com criação/edição inline. Carrega a árvore
 * só quando o curso é expandido — a lista de gestão fica leve.
 */
export function CourseTree({
  courseId,
  providers,
  completionThreshold,
}: CourseTreeProps) {
  const detailQuery = useAdminCourseDetail(courseId);
  const [editing, setEditing] = useState<Editing>(null);

  if (detailQuery.isPending) {
    return <div className="h-24 animate-pulse rounded-xl bg-muted" />;
  }
  if (!detailQuery.isSuccess) {
    return (
      <p className="text-sm text-destructive">Não foi possível carregar os módulos.</p>
    );
  }

  const { modules } = detailQuery.data;
  const nextModuleOrder = Math.max(0, ...modules.map((m) => m.order)) + 1;
  const close = () => setEditing(null);

  return (
    <div className="flex flex-col gap-3">
      {modules.map((module) => {
        const nextLessonOrder = Math.max(0, ...module.lessons.map((l) => l.order)) + 1;
        const isEditingModule =
          editing?.kind === "module" && editing.module?.id === module.id;
        const isAddingLesson =
          editing?.kind === "lesson" && editing.moduleId === module.id && !editing.lesson;

        return (
          <div key={module.id} className="rounded-xl border">
            {isEditingModule ? (
              <div className="p-2">
                <ModuleForm
                  courseId={courseId}
                  module={module}
                  suggestedOrder={module.order}
                  onClose={close}
                />
              </div>
            ) : (
              <div className="flex items-start justify-between gap-3 px-4 py-3">
                <div className="min-w-0">
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Módulo {module.order}
                  </p>
                  <p className="font-medium">{module.title}</p>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setEditing({ kind: "module", module })}
                  aria-label={`Editar módulo ${module.title}`}
                >
                  <Pencil className="size-4" aria-hidden="true" />
                </Button>
              </div>
            )}

            <ul className="divide-y divide-border/60 border-t">
              {module.lessons.map((lesson) => {
                const isEditingLesson =
                  editing?.kind === "lesson" && editing.lesson?.id === lesson.id;
                return (
                  <li
                    key={lesson.id}
                    className={cn("px-4 py-2", isEditingLesson && "py-3")}
                  >
                    {isEditingLesson ? (
                      <LessonForm
                        courseId={courseId}
                        moduleId={module.id}
                        lesson={lesson}
                        suggestedOrder={lesson.order}
                        providers={providers}
                        completionThreshold={completionThreshold}
                        onClose={close}
                      />
                    ) : (
                      <div className="flex items-center gap-3">
                        <span className="w-6 shrink-0 text-xs tabular-nums text-muted-foreground">
                          {lesson.order}.
                        </span>
                        <div className="min-w-0 flex-1">
                          <p
                            className={cn(
                              "text-sm",
                              !lesson.is_active && "text-muted-foreground",
                            )}
                          >
                            {lesson.title}
                            {!lesson.is_active ? (
                              <EyeOff
                                className="ml-1.5 inline size-3.5"
                                aria-label="Inativa"
                              />
                            ) : null}
                          </p>
                          <p className="truncate text-xs text-muted-foreground">
                            {formatDuration(lesson.duration_seconds)} · {lesson.video_ref}
                          </p>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() =>
                            setEditing({ kind: "lesson", moduleId: module.id, lesson })
                          }
                          aria-label={`Editar aula ${lesson.title}`}
                        >
                          <Pencil className="size-4" aria-hidden="true" />
                        </Button>
                      </div>
                    )}
                  </li>
                );
              })}

              <li className="px-4 py-2">
                {isAddingLesson ? (
                  <LessonForm
                    courseId={courseId}
                    moduleId={module.id}
                    suggestedOrder={nextLessonOrder}
                    providers={providers}
                    completionThreshold={completionThreshold}
                    onClose={close}
                  />
                ) : (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="gap-1.5 text-muted-foreground"
                    onClick={() => setEditing({ kind: "lesson", moduleId: module.id })}
                  >
                    <Plus className="size-4" aria-hidden="true" />
                    Nova aula
                  </Button>
                )}
              </li>
            </ul>
          </div>
        );
      })}

      {editing?.kind === "module" && !editing.module ? (
        <ModuleForm
          courseId={courseId}
          suggestedOrder={nextModuleOrder}
          onClose={close}
        />
      ) : (
        <Button
          size="sm"
          variant="outline"
          className="w-fit gap-1.5"
          onClick={() => setEditing({ kind: "module" })}
        >
          <Plus className="size-4" aria-hidden="true" />
          Novo módulo
        </Button>
      )}
    </div>
  );
}
