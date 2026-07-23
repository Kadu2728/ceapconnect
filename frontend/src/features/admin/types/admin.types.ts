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
