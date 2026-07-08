import { apiClient } from "@/lib/axios";

import type {
  CompleteMissionResult,
  MissionList,
} from "@/features/missions/types/mission.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Missões — única camada autorizada a falar com `apiClient`
 * neste domínio. Hooks consomem estas funções; componentes nunca importam
 * `apiClient` diretamente.
 */
const MISSIONS_ENDPOINT = "/api/v1/missions";

export async function fetchMissions(): Promise<MissionList> {
  const { data } = await apiClient.get<ApiEnvelope<MissionList>>(MISSIONS_ENDPOINT);
  return data.data;
}

export async function completeMission(missionId: string): Promise<CompleteMissionResult> {
  const { data } = await apiClient.post<ApiEnvelope<CompleteMissionResult>>(
    `${MISSIONS_ENDPOINT}/${missionId}/complete`,
  );
  return data.data;
}
