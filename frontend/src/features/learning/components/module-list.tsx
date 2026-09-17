"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";

import { LessonRow } from "@/features/learning/components/lesson-row";
import type { ModuleSummary } from "@/features/learning/types/learning.types";
import { cn } from "@/lib/utils";

interface ModuleListProps {
  modules: ModuleSummary[];
  lessonHref: (lessonId: string) => string;
  /** Módulo aberto por padrão — o da próxima aula, para a pessoa não procurar. */
  defaultOpenModuleId: string | null;
}

/**
 * Módulos do curso em accordion — só as aulas do módulo aberto são
 * renderizadas. Num curso com dezenas de aulas, isso é a diferença entre uma
 * lista leve e uma página que trava num celular de entrada.
 *
 * Renderização condicional (não `display: none`): módulo fechado não custa
 * DOM nenhum.
 */
export function ModuleList({
  modules,
  lessonHref,
  defaultOpenModuleId,
}: ModuleListProps) {
  const [openId, setOpenId] = useState<string | null>(
    defaultOpenModuleId ?? modules[0]?.id ?? null,
  );

  if (modules.length === 0) {
    return (
      <p className="rounded-2xl border border-dashed p-6 text-center text-sm text-muted-foreground">
        Nenhuma aula disponível no momento.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {modules.map((module) => {
        const isOpen = module.id === openId;
        const total = module.lessons.length;
        const panelId = `module-${module.id}`;

        return (
          <section key={module.id} className="rounded-2xl border bg-card shadow-sm">
            <button
              type="button"
              aria-expanded={isOpen}
              aria-controls={panelId}
              onClick={() => setOpenId(isOpen ? null : module.id)}
              className="flex w-full items-center gap-4 px-5 py-4 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-2xl"
            >
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Módulo {String(module.order).padStart(2, "0")}
                </p>
                <h3 className="mt-0.5 font-semibold text-pretty">{module.title}</h3>
                {module.description ? (
                  <p className="mt-1 text-sm text-muted-foreground">
                    {module.description}
                  </p>
                ) : null}
              </div>

              <span className="shrink-0 text-sm tabular-nums text-muted-foreground">
                {module.completed_count}/{total}
              </span>
              <ChevronDown
                className={cn(
                  "size-5 shrink-0 text-muted-foreground transition-transform motion-reduce:transition-none",
                  isOpen && "rotate-180",
                )}
                aria-hidden="true"
              />
            </button>

            {isOpen ? (
              <div id={panelId} className="border-t px-2 pb-2 pt-1">
                {module.lessons.map((lesson) => (
                  <LessonRow
                    key={lesson.id}
                    lesson={lesson}
                    href={lessonHref(lesson.id)}
                  />
                ))}
              </div>
            ) : null}
          </section>
        );
      })}
    </div>
  );
}
