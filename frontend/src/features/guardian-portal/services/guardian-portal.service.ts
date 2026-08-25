import { apiClient } from "@/lib/axios";

import type { GuardianPortalView } from "@/features/guardian-portal/types/guardian-portal.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service do Portal do Responsável — única camada autorizada a falar com
 * `apiClient` neste domínio. Sem token de sessão (o responsável não tem
 * conta): a autorização é a posse do `token` do link mágico, na própria URL.
 */
const GUARDIAN_PORTAL_ENDPOINT = "/api/v1/guardian-portal";

export async function fetchGuardianPortal(token: string): Promise<GuardianPortalView> {
  const { data } = await apiClient.get<ApiEnvelope<GuardianPortalView>>(
    `${GUARDIAN_PORTAL_ENDPOINT}/${token}`,
  );
  return data.data;
}

export async function confirmGuardianTraining(
  token: string,
): Promise<GuardianPortalView> {
  const { data } = await apiClient.post<ApiEnvelope<GuardianPortalView>>(
    `${GUARDIAN_PORTAL_ENDPOINT}/${token}/confirm`,
  );
  return data.data;
}
