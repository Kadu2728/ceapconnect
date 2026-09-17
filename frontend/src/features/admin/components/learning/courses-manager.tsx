"use client";

import { ChevronDown, EyeOff, GraduationCap, Pencil, Plus } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CourseForm } from "@/features/admin/components/learning/course-form";
import { CourseTree } from "@/features/admin/components/learning/course-tree";
import type {
  AdminCourse,
  AdminCourseList,
} from "@/features/admin/types/admin-learning.types";
import { cn } from "@/lib/utils";

interface CoursesManagerProps {
  data: AdminCourseList;
}

const AUDIENCE_SHORT: Record<AdminCourse["audience"], string> = {
  guardian: "Responsáveis",
  candidate: "Alunos",
};

/**
 * Gestão de cursos no painel — mesmo desenho de `RewardsManager`: lista,
 * formulário inline, ativa/desativa. Expandir um curso carrega a árvore de
 * módulos e aulas sob demanda.
 */
export function CoursesManager({ data }: CoursesManagerProps) {
  const [editing, setEditing] = useState<AdminCourse | "new" | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  return (
    <Card className="gap-4">
      <div className="flex items-center justify-between gap-3 px-6">
        <div className="flex items-center gap-2">
          <GraduationCap className="size-5 text-brand" aria-hidden="true" />
          <div>
            <h2 className="font-semibold">Videoaulas</h2>
            <p className="text-sm text-muted-foreground">
              {data.courses.length} {data.courses.length === 1 ? "curso" : "cursos"} ·{" "}
              {data.courses.filter((c) => c.is_active).length} ativo(s)
            </p>
          </div>
        </div>
        {editing === null ? (
          <Button size="sm" onClick={() => setEditing("new")}>
            <Plus className="size-4" aria-hidden="true" />
            Novo curso
          </Button>
        ) : null}
      </div>

      {editing === "new" ? (
        <div className="px-6">
          <CourseForm audiences={data.audiences} onClose={() => setEditing(null)} />
        </div>
      ) : null}

      <ul className="divide-y divide-border/60">
        {data.courses.map((course) => {
          const isExpanded = expandedId === course.id;
          const isEditing =
            editing !== null && editing !== "new" && editing.id === course.id;

          return (
            <li key={course.id} className="px-6 py-4">
              {isEditing ? (
                <CourseForm
                  course={course}
                  audiences={data.audiences}
                  onClose={() => setEditing(null)}
                />
              ) : (
                <div className="flex items-start gap-3">
                  <button
                    type="button"
                    aria-expanded={isExpanded}
                    onClick={() => setExpandedId(isExpanded ? null : course.id)}
                    className="flex min-w-0 flex-1 items-start gap-3 text-left"
                  >
                    <ChevronDown
                      className={cn(
                        "mt-1 size-4 shrink-0 text-muted-foreground transition-transform motion-reduce:transition-none",
                        isExpanded && "rotate-180",
                      )}
                      aria-hidden="true"
                    />
                    <div className="min-w-0">
                      <p className="flex flex-wrap items-center gap-2 font-medium">
                        {course.title}
                        <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-normal text-muted-foreground">
                          {AUDIENCE_SHORT[course.audience]}
                        </span>
                        {!course.is_active ? (
                          <span className="inline-flex items-center gap-1 text-xs font-normal text-muted-foreground">
                            <EyeOff className="size-3.5" aria-hidden="true" />
                            Inativo
                          </span>
                        ) : null}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        /{course.slug} · {course.module_count} módulo(s) ·{" "}
                        {course.lesson_count} aula(s)
                      </p>
                    </div>
                  </button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setEditing(course)}
                    aria-label={`Editar curso ${course.title}`}
                  >
                    <Pencil className="size-4" aria-hidden="true" />
                  </Button>
                </div>
              )}

              {isExpanded && !isEditing ? (
                <div className="mt-4 pl-7">
                  <CourseTree
                    courseId={course.id}
                    providers={data.providers}
                    completionThreshold={data.completion_threshold}
                  />
                </div>
              ) : null}
            </li>
          );
        })}
      </ul>
    </Card>
  );
}
