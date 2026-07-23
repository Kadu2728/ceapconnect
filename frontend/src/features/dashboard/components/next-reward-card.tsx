import { ArrowRight, Gift, Lock, Sparkles } from "lucide-react";
import Link from "next/link";
import { createElement } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { DashboardNextReward } from "@/features/dashboard/types/dashboard.types";
import { resolveRewardIcon } from "@/features/rewards/utils/reward-icons";
import { cn } from "@/lib/utils";

interface NextRewardCardProps {
  reward: DashboardNextReward | null;
}

/**
 * Teaser da recompensa em destaque no Dashboard — a ponte entre esforço e
 * prêmio real. `available`: comemora o desbloqueio e chama para resgatar;
 * `locked`: mostra a meta ("Alcance o Nível X"). Sempre leva à tela dedicada,
 * onde o resgate acontece — o Dashboard não duplica a regra de resgate.
 */
export function NextRewardCard({ reward }: NextRewardCardProps) {
  if (reward === null) {
    return (
      <Card className="gap-2">
        <div className="flex items-center gap-2 px-6">
          <Gift className="size-5 text-brand" aria-hidden="true" />
          <h3 className="font-semibold">Recompensas</h3>
        </div>
        <p className="px-6 text-sm text-muted-foreground">
          Você já resgatou todas as recompensas disponíveis. Continue avançando — novas
          recompensas aparecem conforme você sobe de nível.
        </p>
        <div className="px-6">
          <Button asChild variant="outline" size="sm">
            <Link href="/recompensas">Ver recompensas</Link>
          </Button>
        </div>
      </Card>
    );
  }

  const isAvailable = reward.status === "available";

  return (
    <Card
      className={cn(
        "gap-4",
        isAvailable &&
          "border-brand/40 bg-gradient-to-br from-brand/[0.05] to-brand-green/[0.05]",
      )}
    >
      <div className="flex items-center justify-between px-6">
        <span className="inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground">
          <Gift className="size-4 text-brand" aria-hidden="true" />
          {isAvailable ? "Recompensa liberada!" : "Próxima recompensa"}
        </span>
        {isAvailable ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-brand/10 px-2.5 py-1 text-xs font-semibold text-brand">
            <Sparkles className="size-3" aria-hidden="true" />
            Disponível
          </span>
        ) : null}
      </div>

      <div className="flex items-start gap-3 px-6">
        <span
          className={cn(
            "flex size-12 shrink-0 items-center justify-center rounded-2xl",
            isAvailable
              ? "bg-gradient-to-br from-brand/15 to-brand-green/15 text-brand"
              : "bg-muted text-muted-foreground",
          )}
        >
          {createElement(resolveRewardIcon(reward.icon), {
            className: "size-6",
            "aria-hidden": true,
          })}
        </span>
        <div className="min-w-0">
          <h3 className="font-semibold">{reward.title}</h3>
          <p className="text-sm text-muted-foreground">{reward.provider}</p>
          {!isAvailable ? (
            <p className="mt-1 inline-flex items-center gap-1.5 text-xs text-muted-foreground">
              <Lock className="size-3" aria-hidden="true" />
              {reward.requirement_label}
            </p>
          ) : null}
        </div>
      </div>

      <div className="px-6">
        <Button asChild size="sm" variant={isAvailable ? "default" : "outline"}>
          <Link href="/recompensas">
            {isAvailable ? "Resgatar agora" : "Ver recompensas"}
            <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </Button>
      </div>
    </Card>
  );
}
