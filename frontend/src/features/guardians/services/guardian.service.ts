import { apiClient } from "@/lib/axios";

import type {
  GuardianInterventionCreateInput,
  GuardianInterventionItem,
  GuardianMilestoneItem,
  GuardiansAtRiskResponse,
} from "@/features/guardians/types/guardian.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service do alvo "responsável" — única camada autorizada a falar com
 * `apiClient` neste domínio (mesmo padrão de `features/risk`).
 */
const AT_RISK_ENDPOINT = "/api/v1/admin/guardians/at-risk";
const INTERVENTIONS_ENDPOINT = "/api/v1/admin/guardians/interventions";

function trainingConfirmedEndpoint(guardianId: string): string {
  return `/api/v1/admin/guardians/${guardianId}/training-confirmed`;
}

function trainingAttendedEndpoint(guardianId: string): string {
  return `/api/v1/admin/guardians/${guardianId}/training-attended`;
}

function cohortTrainingDateEndpoint(cohortId: string): string {
  return `/api/v1/admin/cohorts/${cohortId}/guardian-training-date`;
}

export async function fetchGuardiansAtRisk(): Promise<GuardiansAtRiskResponse> {
  const { data } =
    await apiClient.get<ApiEnvelope<GuardiansAtRiskResponse>>(AT_RISK_ENDPOINT);
  return data.data;
}

export async function createGuardianIntervention(
  input: GuardianInterventionCreateInput,
): Promise<GuardianInterventionItem> {
  const { data } = await apiClient.post<ApiEnvelope<GuardianInterventionItem>>(
    INTERVENTIONS_ENDPOINT,
    input,
  );
  return data.data;
}

export async function markTrainingConfirmed(
  guardianId: string,
): Promise<GuardianMilestoneItem> {
  const { data } = await apiClient.post<ApiEnvelope<GuardianMilestoneItem>>(
    trainingConfirmedEndpoint(guardianId),
  );
  return data.data;
}

export async function markTrainingAttended(
  guardianId: string,
): Promise<GuardianMilestoneItem> {
  const { data } = await apiClient.post<ApiEnvelope<GuardianMilestoneItem>>(
    trainingAttendedEndpoint(guardianId),
  );
  return data.data;
}

export async function setCohortTrainingDate(
  cohortId: string,
  guardianTrainingDate: string | null,
): Promise<void> {
  await apiClient.patch(cohortTrainingDateEndpoint(cohortId), {
    guardian_training_date: guardianTrainingDate,
  });
}
