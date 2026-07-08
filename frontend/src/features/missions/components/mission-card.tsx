import { CalendarClock, Check, Target, Zap } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { Mission } from "@/features/missions/types/mission.types";
import { cn } from "@/lib/utils";

function formatDueDate(iso: string): string {
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short" }).format(
    new Date(iso),
  );
}

interface MissionCardProps {
  mission: Mission;
  onComplete: () => void;
  isCompleting: boolean;
}

/**
 * Card de uma missão. Pendente: ação clara "Concluir missão". Concluída:
 * estado calmo (marca verde + título riscado), sem ação — a recompensa já
 * aconteceu. Fecha o ciclo "o que faço agora?" do USER_FLOW.
 */
export function MissionCard({ mission, onComplete, isCompleting }: MissionCardProps) {
  const completed = mission.status === "completed";

  return (
    <Card className={cn("gap-4", completed && "bg-muted/40")}>
      <div className="flex items-start gap-4 px-6">
        <span
          className={cn(
            "flex size-11 shrink-0 items-center justify-center rounded-xl",
            completed ? "bg-success/15 text-success" : "bg-brand/10 text-brand",
          )}
        >
          {completed ? (
            <Check className="size-5" aria-hidden="true" />
          ) : (
            <Target className="size-5" aria-hidden="true" />
          )}
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <h3
              className={cn(
                "font-semibold",
                completed && "text-muted-foreground line-through",
              )}
            >
              {mission.title}
            </h3>
            <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-accent px-2.5 py-1 text-xs font-semibold text-accent-foreground">
              <Zap className="size-3" aria-hidden="true" />
              {mission.xp_reward} XP
            </span>
          </div>

          <p className="mt-1 text-sm text-muted-foreground">{mission.description}</p>

          {mission.due_date && !completed ? (
            <p className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground">
              <CalendarClock className="size-3.5" aria-hidden="true" />
              Até {formatDueDate(mission.due_date)}
            </p>
          ) : null}
        </div>
      </div>

      <div className="px-6">
        {completed ? (
          <span className="inline-flex items-center gap-1.5 text-sm font-medium text-success">
            <Check className="size-4" aria-hidden="true" />
            Concluída
          </span>
        ) : (
          <Button
            size="sm"
            onClick={onComplete}
            disabled={isCompleting}
            className="w-full sm:w-auto"
          >
            {isCompleting ? "Concluindo…" : "Concluir missão"}
          </Button>
        )}
      </div>
    </Card>
  );
}
