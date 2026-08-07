import { apiClient } from "@/lib/axios";

import type {
  CandidateRiskDetail,
  InterventionCreateInput,
  InterventionItem,
  RiskQueueResponse,
  RiskTier,
} from "@/features/risk/types/risk.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service do Console de Intervenção — única camada autorizada a falar com
 * `apiClient` neste domínio.
 */
const RISK_QUEUE_ENDPOINT = "/api/v1/admin/risk/queue";
const INTERVENTIONS_ENDPOINT = "/api/v1/admin/interventions";

function candidateRiskEndpoint(candidateProfileId: string): string {
  return `/api/v1/admin/candidates/${candidateProfileId}/risk`;
}

export interface FetchRiskQueueParams {
  cohortId?: string;
  tier?: RiskTier;
}

export async function fetchRiskQueue(
  params: FetchRiskQueueParams = {},
): Promise<RiskQueueResponse> {
  const { data } = await apiClient.get<ApiEnvelope<RiskQueueResponse>>(
    RISK_QUEUE_ENDPOINT,
    {
      params: { cohort_id: params.cohortId, tier: params.tier },
    },
  );
  return data.data;
}

export async function fetchCandidateRisk(
  candidateProfileId: string,
): Promise<CandidateRiskDetail> {
  const { data } = await apiClient.get<ApiEnvelope<CandidateRiskDetail>>(
    candidateRiskEndpoint(candidateProfileId),
  );
  return data.data;
}

export async function createIntervention(
  input: InterventionCreateInput,
): Promise<InterventionItem> {
  const { data } = await apiClient.post<ApiEnvelope<InterventionItem>>(
    INTERVENTIONS_ENDPOINT,
    input,
  );
  return data.data;
}
