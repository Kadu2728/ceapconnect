"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Gift } from "lucide-react";

import { LevelHeader } from "@/features/rewards/components/level-header";
import { RewardCard } from "@/features/rewards/components/reward-card";
import { useRedeemReward } from "@/features/rewards/hooks/use-redeem-reward";
import type { RewardList } from "@/features/rewards/types/reward.types";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface RewardsContentProps {
  data: RewardList;
}

/**
 * Composição da tela de Recompensas: herói de nível + resumo + grid de cards
 * (1 → 2 → 3 colunas) com entrada escalonada. O resgate é orquestrado aqui e
 * repassado a cada card; o card em resgate desabilita apenas o próprio botão.
 */
export function RewardsContent({ data }: RewardsContentProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  const redeemMutation = useRedeemReward();
  const redeemingId = redeemMutation.isPending ? redeemMutation.variables : null;

  return (
    <div className="flex flex-col gap-6">
      <LevelHeader level={data.level} />

      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Gift className="size-4 text-brand" aria-hidden="true" />
        <span>
          <span className="font-semibold text-foreground">{data.summary.unlocked}</span>{" "}
          de {data.summary.total} recompensas desbloqueadas
          {data.summary.redeemed > 0 ? ` · ${data.summary.redeemed} resgatada(s)` : null}
        </span>
      </div>

      <motion.ul
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        {data.rewards.map((reward) => (
          <motion.li key={reward.id} variants={itemVariants} className="h-full">
            <RewardCard
              reward={reward}
              onRedeem={(rewardId) => redeemMutation.mutate(rewardId)}
              isRedeeming={redeemingId === reward.id}
            />
          </motion.li>
        ))}
      </motion.ul>
    </div>
  );
}
