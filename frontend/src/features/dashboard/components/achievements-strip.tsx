import { Trophy } from "lucide-react";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { InlineEmptyState } from "@/features/dashboard/components/inline-empty-state";
import type { DashboardAchievement } from "@/features/dashboard/types/dashboard.types";
import { resolveAchievementIcon } from "@/features/dashboard/utils/achievement-icons";
import { formatFullDate } from "@/features/dashboard/utils/date";

interface AchievementsStripProps {
  achievements: DashboardAchievement[];
}

/**
 * Tira horizontal com as conquistas mais recentes do candidato (EPIC 03).
 * Rolagem horizontal em vez de grid — prioriza as mais recentes sem exigir
 * altura extra da página, e escala bem tanto para 2 quanto para 20 itens.
 */
export function AchievementsStrip({ achievements }: AchievementsStripProps) {
  return (
    <DashboardCard>
      <h2 className="text-base font-semibold">Conquistas recentes</h2>

      {achievements.length === 0 ? (
        <InlineEmptyState
          icon={Trophy}
          message="Nenhuma conquista ainda. Complete missões para desbloquear as primeiras."
        />
      ) : (
        <ul className="mt-5 flex gap-4 overflow-x-auto pb-1">
          {achievements.map((achievement) => {
            const Icon = resolveAchievementIcon(achievement.icon);

            return (
              <li
                key={achievement.id}
                title={achievement.description}
                className="flex w-28 shrink-0 flex-col items-center gap-2 text-center"
              >
                <span className="flex size-14 items-center justify-center rounded-full bg-accent text-accent-foreground">
                  <Icon className="size-6" aria-hidden="true" />
                </span>
                <span className="text-xs font-medium">{achievement.name}</span>
                <span className="text-[11px] text-muted-foreground">
                  {formatFullDate(achievement.unlocked_at)}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </DashboardCard>
  );
}
