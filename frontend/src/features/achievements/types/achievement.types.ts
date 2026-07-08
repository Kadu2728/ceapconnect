/**
 * Contratos da feature Conquistas (EPIC 06), espelhando o backend
 * (`GET /api/v1/achievements`). Campos em `snake_case` mantidos como enviados.
 */

export interface Achievement {
  id: string;
  name: string;
  description: string;
  /** Nome de ícone `lucide-react` (ver `dashboard/utils/achievement-icons.ts`). */
  icon: string;
  unlocked: boolean;
  unlocked_at: string | null;
}

export interface AchievementSummary {
  total: number;
  unlocked: number;
}

export interface AchievementList {
  achievements: Achievement[];
  summary: AchievementSummary;
}
