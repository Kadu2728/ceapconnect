/**
 * Contratos do RBAC do responsável (conta própria, autenticada), espelhando
 * `app.schemas.guardian_access` no backend. Reaproveita `DashboardJourney`
 * (`features/dashboard/types/dashboard.types.ts`) para a jornada — mesmo
 * shape (`JourneyProgress`) usado tanto pelo Dashboard do candidato quanto
 * aqui, sem necessidade de um tipo novo.
 */
import type { DashboardJourney } from "@/features/dashboard/types/dashboard.types";

export interface GuardianChildItem {
  candidate_profile_id: string;
  name: string;
  current_step_label: string;
  journey_percentage: number;
}

export interface GuardianChildrenResponse {
  children: GuardianChildItem[];
}

export interface GuardianChildJourneyResponse {
  candidate_name: string;
  journey: DashboardJourney;
  pending_required_documents: number;
  exam_date: string | null;
  exam_location: string;
  interview_date: string | null;
  interview_location: string;
  guardian_training_date: string | null;
  guardian_training_confirmed: boolean;
  guardian_training_attended: boolean;
}

export interface GuardianLinkChildRequest {
  token: string;
}
