"use client";

import { motion, useReducedMotion } from "framer-motion";

import { AchievementsStrip } from "@/features/dashboard/components/achievements-strip";
import { CohortStandingCard } from "@/features/dashboard/components/cohort-standing-card";
import { ExamCountdown } from "@/features/dashboard/components/exam-countdown";
import { Greeting } from "@/features/dashboard/components/greeting";
import { GuardianStatusCard } from "@/features/dashboard/components/guardian-status-card";
import { JourneyProgress } from "@/features/dashboard/components/journey-progress";
import { NextMissionCard } from "@/features/dashboard/components/next-mission-card";
import { NextRewardCard } from "@/features/dashboard/components/next-reward-card";
import { UpcomingEventsList } from "@/features/dashboard/components/upcoming-events-list";
import { XpBadge } from "@/features/dashboard/components/xp-badge";
import type { DashboardData } from "@/features/dashboard/types/dashboard.types";
import { LevelHeader } from "@/features/rewards/components/level-header";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface DashboardContentProps {
  data: DashboardData;
}

/**
 * Composição do Dashboard (EPIC 03) com os dados reais já carregados.
 *
 * Ordem deliberada, do mais para o menos urgente (USER_FLOW.md → perguntas
 * que o Dashboard precisa responder de imediato): saudação + XP → contagem
 * para a prova ("quanto falta") → jornada ("onde estou") → missão do dia
 * ("o que faço agora") → eventos → conquistas (reforço motivacional, por
 * último, nunca competindo com a informação acionável).
 */
export function DashboardContent({ data }: DashboardContentProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="flex flex-col gap-6"
    >
      <motion.div
        variants={itemVariants}
        className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <Greeting name={data.greeting_name} />
        <XpBadge xpTotal={data.xp_total} />
      </motion.div>

      <motion.div variants={itemVariants}>
        <LevelHeader level={data.level} />
      </motion.div>

      <motion.div variants={itemVariants}>
        <ExamCountdown examDate={data.exam_date} />
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="flex flex-col gap-6 lg:col-span-2">
          <motion.div variants={itemVariants}>
            <JourneyProgress journey={data.journey} />
          </motion.div>
          <motion.div variants={itemVariants}>
            <NextMissionCard mission={data.next_mission} />
          </motion.div>
          <motion.div variants={itemVariants}>
            <NextRewardCard reward={data.next_reward} />
          </motion.div>
        </div>

        <motion.div variants={itemVariants}>
          <UpcomingEventsList events={data.upcoming_events} />
        </motion.div>
      </div>

      <motion.div variants={itemVariants}>
        <AchievementsStrip achievements={data.recent_achievements} />
      </motion.div>

      <motion.div variants={itemVariants}>
        <CohortStandingCard standing={data.cohort_standing} />
      </motion.div>

      <motion.div variants={itemVariants}>
        <GuardianStatusCard status={data.guardian_status} />
      </motion.div>
    </motion.div>
  );
}
