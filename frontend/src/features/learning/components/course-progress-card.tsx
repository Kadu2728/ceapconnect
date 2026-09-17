"use client";

import { motion, useReducedMotion } from "framer-motion";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";

interface CourseProgressCardProps {
  progressPercent: number;
  completedLessons: number;
  totalLessons: number;
}

/**
 * "Seu progresso" — o número que responde "quanto já avancei". Calculado
 * no backend a partir das aulas concluídas; aqui só exibição.
 */
export function CourseProgressCard({
  progressPercent,
  completedLessons,
  totalLessons,
}: CourseProgressCardProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const percent = Math.min(100, Math.max(0, progressPercent));
  const isComplete = totalLessons > 0 && completedLessons === totalLessons;

  return (
    <DashboardCard>
      <div className="flex items-baseline justify-between gap-4">
        <h2 className="text-base font-semibold">Seu progresso</h2>
        <span className="text-2xl font-bold tabular-nums text-primary">{percent}%</span>
      </div>

      <div
        role="progressbar"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Progresso na formação"
        className="mt-4 h-2 w-full overflow-hidden rounded-full bg-muted"
      >
        <motion.div
          className="h-full rounded-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: shouldReduceMotion ? 0 : 0.6, ease: "easeOut" }}
        />
      </div>

      <p className="mt-3 text-sm text-muted-foreground">
        {isComplete ? (
          <span className="font-medium text-success">Formação concluída — parabéns!</span>
        ) : (
          <>
            <span className="font-medium text-foreground">{completedLessons}</span> de{" "}
            {totalLessons} {totalLessons === 1 ? "aula concluída" : "aulas concluídas"}
          </>
        )}
      </p>
    </DashboardCard>
  );
}
