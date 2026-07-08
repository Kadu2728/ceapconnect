"use client";

import { motion, useReducedMotion } from "framer-motion";

import { AchievementCard } from "@/features/achievements/components/achievement-card";
import { AchievementsSummary } from "@/features/achievements/components/achievements-summary";
import type { AchievementList } from "@/features/achievements/types/achievement.types";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface AchievementsContentProps {
  data: AchievementList;
}

/**
 * Composição da tela de Conquistas: resumo + grid de cards (2 → 3 colunas) com
 * entrada escalonada.
 */
export function AchievementsContent({ data }: AchievementsContentProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  return (
    <div className="flex flex-col gap-6">
      <AchievementsSummary summary={data.summary} />

      <motion.ul
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        {data.achievements.map((achievement) => (
          <motion.li key={achievement.id} variants={itemVariants}>
            <AchievementCard achievement={achievement} />
          </motion.li>
        ))}
      </motion.ul>
    </div>
  );
}
