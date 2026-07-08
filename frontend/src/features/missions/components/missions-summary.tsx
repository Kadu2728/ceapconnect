import { Card } from "@/components/ui/card";
import { XpBadge } from "@/features/dashboard/components/xp-badge";
import type { MissionSummary } from "@/features/missions/types/mission.types";

interface MissionsSummaryProps {
  summary: MissionSummary;
}

/**
 * Resumo do progresso em missões: quantas concluídas de quantas + XP total,
 * com barra de progresso na cor de marca. Responde de imediato "quanto falta?".
 */
export function MissionsSummary({ summary }: MissionsSummaryProps) {
  const percentage =
    summary.total > 0 ? Math.round((summary.completed / summary.total) * 100) : 0;

  return (
    <Card className="gap-4">
      <div className="flex items-center justify-between px-6">
        <div>
          <p className="text-sm text-muted-foreground">Missões concluídas</p>
          <p className="text-2xl font-bold tracking-tight">
            {summary.completed}
            <span className="text-lg font-medium text-muted-foreground">
              /{summary.total}
            </span>
          </p>
        </div>
        <XpBadge xpTotal={summary.xp_total} />
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
