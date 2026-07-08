import { Clock, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { InlineEmptyState } from "@/features/dashboard/components/inline-empty-state";
import type { DashboardMission } from "@/features/dashboard/types/dashboard.types";
import { formatFullDate } from "@/features/dashboard/utils/date";

interface NextMissionCardProps {
  mission: DashboardMission | null;
}

/**
 * Card da missão do dia (EPIC 03). Concluir missão é EPIC 05 — por isso o
 * botão fica desabilitado e rotulado "Em breve" em vez de escondido
 * (USER_FLOW.md: "o usuário nunca deve ficar perdido").
 */
export function NextMissionCard({ mission }: NextMissionCardProps) {
  return (
    <DashboardCard className="flex flex-col gap-4">
      <span className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
        Missão do dia
      </span>

      {mission ? (
        <>
          <div className="flex items-start justify-between gap-4">
            <h2 className="text-lg font-semibold">{mission.title}</h2>
            <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-accent px-2.5 py-1 text-xs font-semibold text-accent-foreground">
              +{mission.xp_reward} XP
            </span>
          </div>

          <p className="text-sm text-muted-foreground">{mission.description}</p>

          {mission.due_date ? (
            <p className="text-xs text-muted-foreground">
              Prazo: {formatFullDate(mission.due_date)}
            </p>
          ) : null}

          <Button
            disabled
            variant="secondary"
            className="mt-2 w-full gap-2 sm:w-fit"
            aria-label="Concluir missão — disponível em breve"
          >
            <Clock className="size-4" aria-hidden="true" />
            Em breve
          </Button>
        </>
      ) : (
        <InlineEmptyState
          icon={Sparkles}
          message="Nenhuma missão disponível agora. Volte em breve para novos desafios."
        />
      )}
    </DashboardCard>
  );
}
