/**
 * Contratos da feature Admin (EPIC 10), espelhando `GET /api/v1/admin/overview`.
 */

export interface DailyCount {
  date: string;
  count: number;
}

export interface LevelBucket {
  level: number;
  name: string;
  count: number;
}

export interface TopReward {
  title: string;
  provider: string;
  count: number;
}

/** Impacto das intervenções do Console de Risco nos últimos 30 dias (EPIC 14). */
export interface InterventionImpact {
  total: number;
  measured: number;
  pending_measurement: number;
  /** Negativo = risco caiu em média (bom sinal). Null = ainda sem medições. */
  avg_score_delta: number | null;
  pct_improved: number | null;
  pct_had_activity_after: number | null;
}

export interface AdminOverview {
  total_students: number;
  accessed: number;
  never_accessed: number;
  engagement_rate: number;
  active_24h: number;
  active_7d: number;
  active_30d: number;
  new_7d: number;
  new_30d: number;
  missions_completed: number;
  event_registrations: number;
  achievements_unlocked: number;
  total_xp: number;
  avg_xp: number;
  rewards_redeemed: number;
  rewards_pending: number;
  rewards_fulfilled: number;
  level_distribution: LevelBucket[];
  top_rewards: TopReward[];
  signups_daily: DailyCount[];
  intervention_impact: InterventionImpact;
}

export type RedemptionStatus = "pending" | "fulfilled" | "cancelled";

/** Um resgate de recompensa na fila de entrega (EPIC 13). */
export interface AdminRedemption {
  id: string;
  student_name: string;
  student_email: string;
  reward_title: string;
  reward_provider: string;
  status: RedemptionStatus;
  redeemed_at: string;
  fulfilled_at: string | null;
}

export interface AdminRedemptionList {
  redemptions: AdminRedemption[];
  pending_count: number;
  fulfilled_count: number;
}

export type RewardUnlockType = "level" | "achievement";

/** Uma recompensa na visão de gestão (inclui inativas). */
export interface AdminReward {
  id: string;
  title: string;
  description: string;
  provider: string;
  category: string;
  icon: string;
  unlock_type: RewardUnlockType;
  required_level: number | null;
  required_achievement_id: string | null;
  required_achievement_name: string | null;
  featured: boolean;
  is_active: boolean;
  sort_order: number;
}

export interface AdminAchievementOption {
  id: string;
  name: string;
}

export interface AdminRewardList {
  rewards: AdminReward[];
  achievements: AdminAchievementOption[];
}

/** Corpo de criação/edição de recompensa (envio completo). */
export interface AdminRewardInput {
  title: string;
  description: string;
  provider: string;
  category: string;
  icon: string;
  unlock_type: RewardUnlockType;
  required_level: number | null;
  required_achievement_id: string | null;
  featured: boolean;
  is_active: boolean;
  sort_order: number;
}
