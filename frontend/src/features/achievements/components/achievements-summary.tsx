import { Trophy } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { AchievementSummary } from "@/features/achievements/types/achievement.types";

interface AchievementsSummaryProps {
  summary: AchievementSummary;
}

/**
 * Resumo das conquistas: quantas desbloqueadas de quantas + percentual, com
 * barra de progresso na cor de marca.
 */
export function AchievementsSummary({ summary }: AchievementsSummaryProps) {
  const percentage =
    summary.total > 0 ? Math.round((summary.unlocked / summary.total) * 100) : 0;

  return (
    <Card className="gap-4">
      <div className="flex items-center justify-between px-6">
        <div>
          <p className="text-sm text-muted-foreground">Conquistas desbloqueadas</p>
          <p className="text-2xl font-bold tracking-tight">
            {summary.unlocked}
            <span className="text-lg font-medium text-muted-foreground">
              /{summary.total}
            </span>
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-accent px-3.5 py-1.5 text-sm font-semibold text-accent-foreground">
          <Trophy className="size-4" aria-hidden="true" />
          {percentage}%
        </span>
      </div>

      <div className="px-6">
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-gradient-to-r from-brand to-brand-green transition-[width] duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    </Card>
  );
}
