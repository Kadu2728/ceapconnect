import { apiClient } from "@/lib/axios";

import type {
  GuardianChildItem,
  GuardianChildJourneyResponse,
  GuardianChildrenResponse,
  GuardianLinkChildRequest,
} from "@/features/guardian-access/types/guardian-access.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service do RBAC do responsável (conta própria) — única camada autorizada
 * a falar com `apiClient` neste domínio. Todas as rotas exigem sessão
 * autenticada (`role === "guardian"`), carregada automaticamente pelo
 * interceptor de `apiClient`.
 */
const GUARDIAN_ENDPOINT = "/api/v1/guardian";

export async function fetchGuardianChildren(): Promise<GuardianChildrenResponse> {
  const { data } = await apiClient.get<ApiEnvelope<GuardianChildrenResponse>>(
    `${GUARDIAN_ENDPOINT}/children`,
  );
  return data.data;
}

export async function fetchGuardianChildJourney(
  candidateProfileId: string,
): Promise<GuardianChildJourneyResponse> {
  const { data } = await apiClient.get<ApiEnvelope<GuardianChildJourneyResponse>>(
    `${GUARDIAN_ENDPOINT}/children/${candidateProfileId}/journey`,
  );
  return data.data;
}

export async function linkGuardianChild(
  payload: GuardianLinkChildRequest,
): Promise<GuardianChildItem> {
  const { data } = await apiClient.post<ApiEnvelope<GuardianChildItem>>(
    `${GUARDIAN_ENDPOINT}/link-children`,
    payload,
  );
  return data.data;
}
