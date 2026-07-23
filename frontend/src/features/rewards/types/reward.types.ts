/**
 * Contratos da feature Recompensas (EPIC 13), espelhando o backend
 * (`GET /api/v1/rewards` e `POST /api/v1/rewards/{id}/redeem`). Campos em
 * `snake_case` mantidos como o backend os envia.
 */

/** Nível do candidato e progresso rumo ao próximo (compartilhado com o Dashboard). */
export interface LevelInfo {
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

/**
 * Status da recompensa para o candidato:
 * - `locked`    → condição ainda não atingida;
 * - `available` → desbloqueada, pronta para resgate;
 * - `redeemed`  → resgatada, aguardando entrega;
 * - `fulfilled` → entregue pela equipe.
 */
export type RewardStatus = "locked" | "available" | "redeemed" | "fulfilled";

export type RewardUnlockType = "level" | "achievement";

export interface Reward {
  id: string;
  title: string;
  description: string;
  provider: string;
  category: string;
  /** Nome de ícone `lucide-react` (ver `rewards/utils/reward-icons.ts`). */
  icon: string;
  featured: boolean;
  unlock_type: RewardUnlockType;
  required_level: number | null;
  /** Texto pronto para UI (ex.: "Alcance o Nível 4"). */
  requirement_label: string;
  status: RewardStatus;
  redeemed_at: string | null;
  fulfilled_at: string | null;
}

export interface RewardSummary {
  total: number;
  unlocked: number;
  redeemed: number;
}

export interface RewardList {
  level: LevelInfo;
  rewards: Reward[];
  summary: RewardSummary;
}

export interface RedeemRewardResult {
  reward: Reward;
}
