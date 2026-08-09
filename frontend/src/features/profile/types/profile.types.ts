/**
 * Contratos da Tela de Perfil (EPIC 09), espelhando o backend
 * (`/api/v1/profile`). Campos em `snake_case` como o backend os envia.
 */

import type { LevelInfo } from "@/features/rewards/types/reward.types";

export interface ProfileStats {
  level: LevelInfo;
  missions_completed: number;
  achievements_unlocked: number;
  rewards_redeemed: number;
}

export interface Profile {
  id: string;
  name: string;
  email: string;
  /** CPF mascarado (ex.: "123.***.***-09"). */
  cpf_masked: string;
  phone: string;
  member_since: string;
  stats: ProfileStats;
  /** Entrevista com o responsável (EPIC 17). */
  interview_date: string | null;
  interview_location: string;
  guardian_name: string | null;
  guardian_phone: string | null;
  guardian_email: string | null;
  guardian_notified_at: string | null;
}

export interface ProfileUpdateInput {
  name: string;
  phone: string;
  guardian_name: string | null;
  guardian_phone: string | null;
  guardian_email: string | null;
}

export interface GuardianEmailNoticeResult {
  sent: boolean;
  message: string;
  guardian_notified_at: string | null;
}
