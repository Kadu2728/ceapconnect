/**
 * Contratos do alvo "responsável" do Console de Intervenção (alvo duplo) +
 * Área de Pais, espelhando o backend (`/api/v1/admin/guardians/*`,
 * `/api/v1/admin/cohorts/*`). Campos em `snake_case` como o backend os envia.
 */

export interface GuardianAtRiskItem {
  candidate_profile_id: string;
  candidate_name: string;
  candidate_email: string;
  cohort_id: string | null;
  cohort_name: string | null;
  guardian_id: string | null;
  guardian_name: string | null;
  guardian_phone: string | null;
  guardian_email: string | null;
  training_confirmed_at: string | null;
  training_attended_at: string | null;
  guardian_training_date: string | null;
  reason: string;
}

export interface GuardiansAtRiskResponse {
  items: GuardianAtRiskItem[];
  total: number;
}

export type GuardianInterventionChannel = "call" | "whatsapp" | "other";
export type GuardianInterventionOutcome = "reached" | "no_answer" | "other";

export interface GuardianInterventionCreateInput {
  guardian_id: string;
  channel: GuardianInterventionChannel;
  outcome: GuardianInterventionOutcome;
  notes?: string;
}

export interface GuardianInterventionItem {
  id: string;
  channel: GuardianInterventionChannel;
  outcome: GuardianInterventionOutcome;
  notes: string | null;
  created_by_name: string | null;
  created_at: string;
}

export interface GuardianMilestoneItem {
  guardian_id: string;
  training_confirmed_at: string | null;
  training_attended_at: string | null;
}
