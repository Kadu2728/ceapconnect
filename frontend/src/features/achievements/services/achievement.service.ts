import { apiClient } from "@/lib/axios";

import type { AchievementList } from "@/features/achievements/types/achievement.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Conquistas — única camada autorizada a falar com
 * `apiClient` neste domínio.
 */
const ACHIEVEMENTS_ENDPOINT = "/api/v1/achievements";

export async function fetchAchievements(): Promise<AchievementList> {
  const { data } =
    await apiClient.get<ApiEnvelope<AchievementList>>(ACHIEVEMENTS_ENDPOINT);
  return data.data;
}
