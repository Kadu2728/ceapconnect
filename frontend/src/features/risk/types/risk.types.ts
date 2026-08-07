/**
 * Contratos do Console de Intervenção (EPIC 14 — Predição de evasão),
 * espelhando o backend (`/api/v1/admin/risk/*`, `/api/v1/admin/interventions`).
 * Campos em `snake_case` como o backend os envia.
 */

export type RiskTier = "baixo" | "medio" | "alto";

export interface RiskFactor {
  key: string;
  label: string;
  points: number;
}

export interface RiskQueueItem {
  candidate_profile_id: string;
  candidate_name: string;
  candidate_email: string;
  cohort_id: string | null;
  cohort_name: string | null;
  score: number;
  tier: RiskTier;
  explanation: string;
  computed_at: string;
}

export interface RiskQueueResponse {
  items: RiskQueueItem[];
  total: number;
  counts_by_tier: Record<RiskTier, number>;
}

export interface ActivityTimelineItem {
  name: string;
  props: Record<string, unknown>;
  occurred_at: string;
}

export type InterventionChannel = "call" | "whatsapp" | "other";
export type InterventionOutcome = "reached" | "no_answer" | "other";

export interface InterventionItem {
  id: string;
  channel: InterventionChannel;
  outcome: InterventionOutcome;
  notes: string | null;
  created_by_name: string | null;
  score_at_creation: number;
  created_at: string;
  // Preenchidos ~7 dias depois pelo job (null até lá).
  measured_at: string | null;
  score_after: number | null;
  had_activity_after: boolean | null;
  score_delta: number | null;
}

export interface CandidateRiskDetail {
  candidate_profile_id: string;
  candidate_name: string;
  candidate_email: string;
  cohort_id: string | null;
  cohort_name: string | null;
  score: number | null;
  tier: RiskTier | null;
  factors: RiskFactor[];
  explanation: string | null;
  computed_at: string | null;
  recent_activity: ActivityTimelineItem[];
  interventions: InterventionItem[];
}

export interface InterventionCreateInput {
  candidate_profile_id: string;
  channel: InterventionChannel;
  outcome: InterventionOutcome;
  notes?: string;
}
