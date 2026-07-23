import { Trophy } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { TopReward } from "@/features/admin/types/admin.types";
import { cn } from "@/lib/utils";

interface TopRewardsListProps {
  data: TopReward[];
}

/** Cores da medalha por posição no ranking (ouro, prata, bronze). */
const RANK_STYLES = [
  "bg-brand-orange/15 text-brand-orange",
  "bg-muted text-muted-foreground",
  "bg-brand/10 text-brand",
];

/**
 * Ranking das recompensas mais resgatadas — mostra o que de fato motiva os
 * alunos, ajudando a direção a priorizar o catálogo real de recompensas.
 */
export function TopRewardsList({ data }: TopRewardsListProps) {
  return (
    <Card className="h-full gap-4">
      <div className="flex items-center gap-2 px-6">
        <Trophy className="size-5 text-brand-orange" aria-hidden="true" />
        <div>
          <h3 className="font-semibold">Recompensas mais resgatadas</h3>
          <p className="text-sm text-muted-foreground">O que mais engaja os alunos</p>
        </div>
      </div>

      {data.length === 0 ? (
        <p className="px-6 pb-2 text-sm text-muted-foreground">
          Nenhum resgate ainda. O ranking aparece assim que os alunos começarem a
          resgatar.
        </p>
      ) : (
        <ol className="flex flex-col gap-3 px-6 pb-2">
          {data.map((reward, index) => (
            <li key={`${reward.title}-${index}`} className="flex items-center gap-3">
              <span
                className={cn(
                  "flex size-8 shrink-0 items-center justify-center rounded-lg text-sm font-bold tabular-nums",
                  RANK_STYLES[index] ?? "bg-muted text-muted-foreground",
                )}
              >
                {index + 1}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{reward.title}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {reward.provider}
                </p>
              </div>
              <span className="shrink-0 text-sm font-semibold tabular-nums">
                {reward.count}
                <span className="ml-1 text-xs font-normal text-muted-foreground">
                  resgate(s)
                </span>
              </span>
            </li>
          ))}
        </ol>
      )}
    </Card>
  );
}
