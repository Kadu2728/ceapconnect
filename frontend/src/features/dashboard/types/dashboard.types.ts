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

export interface DashboardData {
  greeting_name: string;
  journey: DashboardJourney;
  xp_total: number;
  next_mission: DashboardMission | null;
  recent_achievements: DashboardAchievement[];
  upcoming_events: DashboardEvent[];
  unread_notifications_count: number;
  exam_date: string | null;
}
