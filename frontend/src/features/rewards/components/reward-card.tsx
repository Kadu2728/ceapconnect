import { Check, Clock, Lock, Sparkles, Star } from "lucide-react";
import { createElement } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { Reward } from "@/features/rewards/types/reward.types";
import { resolveRewardIcon } from "@/features/rewards/utils/reward-icons";
import { cn } from "@/lib/utils";

interface RewardCardProps {
  reward: Reward;
  onRedeem: (rewardId: string) => void;
  isRedeeming: boolean;
}

/**
 * Card de uma recompensa real (curso/certificação). Comunica valor e progresso
 * de imediato:
 * - `available` → destaque de marca + ação "Resgatar recompensa";
 * - `redeemed`/`fulfilled` → estado calmo de acompanhamento (a ação já ocorreu);
 * - `locked`  → esmaecido, com o requisito bem visível (meta, nunca frustração).
 */
export function RewardCard({ reward, onRedeem, isRedeeming }: RewardCardProps) {
  const { status } = reward;
  const isLocked = status === "locked";
  const isAvailable = status === "available";

  return (
    <Card
      className={cn(
        "h-full gap-4 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md",
        isAvailable &&
          "border-brand/40 bg-gradient-to-br from-brand/[0.04] to-brand-green/[0.04]",
        isLocked && "opacity-75",
      )}
    >
      <div className="flex items-start gap-4 px-6">
        <span
          className={cn(
            "flex size-14 shrink-0 items-center justify-center rounded-2xl",
            isLocked
              ? "bg-muted text-muted-foreground"
              : "bg-gradient-to-br from-brand/15 to-brand-green/15 text-brand",
          )}
        >
          {isLocked ? (
            <Lock className="size-6" aria-hidden="true" />
          ) : (
            createElement(resolveRewardIcon(reward.icon), {
              className: "size-7",
              "aria-hidden": true,
            })
          )}
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <p className="min-w-0 truncate text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {reward.category} · {reward.provider}
            </p>
            {reward.featured && !isLocked ? (
              <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-brand-orange/15 px-2 py-0.5 text-[11px] font-semibold text-brand-orange">
                <Star className="size-3" aria-hidden="true" />
                Destaque
              </span>
            ) : null}
          </div>
          <h3 className={cn("mt-0.5 font-semibold", isLocked && "text-muted-foreground")}>
            {reward.title}
          </h3>
        </div>
      </div>

      <p className="px-6 text-sm text-muted-foreground">{reward.description}</p>

      <div className="mt-auto flex items-center justify-between gap-3 px-6">
        <RewardStatusLabel reward={reward} />

        {isAvailable ? (
          <Button
            size="sm"
            onClick={() => onRedeem(reward.id)}
            disabled={isRedeeming}
            className="shrink-0"
          >
            {isRedeeming ? "Resgatando…" : "Resgatar"}
          </Button>
        ) : null}
      </div>
    </Card>
  );
}

/** Rótulo de status/requisito no rodapé do card, coerente com cada estado. */
function RewardStatusLabel({ reward }: { reward: Reward }) {
  switch (reward.status) {
    case "available":
      return (
        <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand">
          <Sparkles className="size-4" aria-hidden="true" />
          Desbloqueada!
        </span>
      );
    case "redeemed":
      return (
        <span className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-orange">
          <Clock className="size-4" aria-hidden="true" />
          Resgatada · aguardando entrega
        </span>
      );
    case "fulfilled":
      return (
        <span className="inline-flex items-center gap-1.5 text-sm font-medium text-success">
          <Check className="size-4" aria-hidden="true" />
          Entregue
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
          <Lock className="size-3.5" aria-hidden="true" />
          {reward.requirement_label}
        </span>
      );
  }
}
