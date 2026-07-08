"use client";

import { motion, useReducedMotion } from "framer-motion";

import { MissionCard } from "@/features/missions/components/mission-card";
import { MissionsSummary } from "@/features/missions/components/missions-summary";
import { useCompleteMission } from "@/features/missions/hooks/use-complete-mission";
import type { MissionList } from "@/features/missions/types/mission.types";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface MissionsContentProps {
  data: MissionList;
}

/**
 * Composição da tela de Missões: resumo de progresso + lista de missões com
 * entrada escalonada. Detém a mutation de conclusão e a repassa a cada card,
 * mantendo os cards puros (regra: interface sem regra de negócio).
 */
export function MissionsContent({ data }: MissionsContentProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  const { mutate, isPending, variables } = useCompleteMission();

  return (
    <div className="flex flex-col gap-6">
      <MissionsSummary summary={data.summary} />

      <motion.ul
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="flex flex-col gap-4"
      >
        {data.missions.map((mission) => (
          <motion.li key={mission.id} variants={itemVariants}>
            <MissionCard
              mission={mission}
              onComplete={() => mutate(mission.id)}
              isCompleting={isPending && variables === mission.id}
            />
          </motion.li>
        ))}
      </motion.ul>
    </div>
  );
}
