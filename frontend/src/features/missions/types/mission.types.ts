/**
 * Contratos da feature Missões (EPIC 05), espelhando o backend
 * (`GET /api/v1/missions`, `POST /api/v1/missions/{id}/complete`). Campos em
 * `snake_case` são mantidos como o backend envia.
 */

export type MissionStatus = "pending" | "completed";

export interface Mission {
  id: string;
  title: string;
  description: string;
  xp_reward: number;
  due_date: string | null;
  status: MissionStatus;
  completed_at: string | null;
}

export interface MissionSummary {
  total: number;
  completed: number;
  xp_total: number;
}

export interface MissionList {
  missions: Mission[];
  summary: MissionSummary;
}

export interface UnlockedAchievement {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface CompleteMissionResult {
  mission: Mission;
  xp_gained: number;
  xp_total: number;
  unlocked_achievements: UnlockedAchievement[];
}
