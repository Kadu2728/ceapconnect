import { apiClient } from "@/lib/axios";

import type {
  CandidateState,
  CandidateTrackableEvent,
  NextBestAction,
} from "@/features/journey-os/types/journey-os.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service do Candidate Journey OS — única camada autorizada a chamar
 * `apiClient` para este domínio (mesmo padrão de `dashboard.service.ts`).
 */
const CANDIDATE_STATE_ENDPOINT = "/api/v1/candidate-state";
const NEXT_BEST_ACTION_ENDPOINT = "/api/v1/next-best-action";

export async function fetchCandidateState(): Promise<CandidateState> {
  const { data } = await apiClient.get<ApiEnvelope<CandidateState>>(
    CANDIDATE_STATE_ENDPOINT,
  );
  return data.data;
}

export async function fetchNextBestAction(): Promise<NextBestAction | null> {
  const { data } = await apiClient.get<ApiEnvelope<NextBestAction | null>>(
    NEXT_BEST_ACTION_ENDPOINT,
  );
  return data.data;
}

/**
 * Telemetria best-effort — mesma garantia do backend
 * (`activity_event_service`): nunca deve travar nem exibir erro ao
 * candidato se falhar. Quem chama não deve reagir à rejeição desta promise.
 */
export async function trackCandidateEvent(
  name: CandidateTrackableEvent,
  props: Record<string, unknown> = {},
): Promise<void> {
  await apiClient.post(`${CANDIDATE_STATE_ENDPOINT}/events`, { name, props });
}
