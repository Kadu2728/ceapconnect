/**
 * Contratos de resposta da API do Dashboard (EPIC 03), espelhando
 * exatamente o contrato acordado com o backend. Nomes de campo em
 * `snake_case` são mantidos como o backend os envia — a conversão para o
 * formato usado internamente pela UI acontece nos componentes/utils, nunca
 * aqui.
 */

export type JourneyStepStatus = "completed" | "current" | "pending";

export interface JourneyStep {
  key: string;
  label: string;
  status: JourneyStepStatus;
}

export interface DashboardJourney {
  percentage: number;
  current_step_key: string;
  steps: JourneyStep[];
}

export interface DashboardMission {
  id: string;
  title: string;
  description: string;
  xp_reward: number;
  due_date: string | null;
}

export interface DashboardAchievement {
  id: string;
  name: string;
  description: string;
  /** Nome de ícone do `lucide-react` (ex.: "trophy", "star") — ver `utils/achievement-icons.ts`. */
  icon: string;
  unlocked_at: string;
}

export interface DashboardEvent {
  id: string;
  title: string;
  date: string;
  location: string;
}

/** Nível atual do candidato e progresso rumo ao próximo (gamificação — EPIC 13). */
export interface DashboardLevel {
  level: number;
  name: string;
  xp_total: number;
  current_level_xp: number;
  next_level_xp: number | null;
  xp_into_level: number;
  xp_to_next: number | null;
  progress_percentage: number;
  is_max_level: boolean;
}

/** Recompensa em destaque no Dashboard (a resgatar ou a mirar). */
export interface DashboardNextReward {
  id: string;
  title: string;
  provider: string;
  /** Nome de ícone `lucide-react` (ver `rewards/utils/reward-icons.ts`). */
  icon: string;
  status: "available" | "locked";
  requirement_label: string;
}

/** Faixa de engajamento na coorte, sem posição nominal (EPIC 20). */
export interface DashboardCohortStanding {
  cohort_size: number;
  /** 10/25/50 = "entre os N% mais engajados"; null = mensagem de progresso pessoal. */
  top_percent: number | null;
  message: string;
}

export interface DashboardData {
  greeting_name: string;
  journey: DashboardJourney;
  xp_total: number;
  level: DashboardLevel;
  next_reward: DashboardNextReward | null;
  next_mission: DashboardMission | null;
  recent_achievements: DashboardAchievement[];
  upcoming_events: DashboardEvent[];
  unread_notifications_count: number;
  exam_date: string | null;
  onboarded: boolean;
  cohort_standing: DashboardCohortStanding | null;
}
