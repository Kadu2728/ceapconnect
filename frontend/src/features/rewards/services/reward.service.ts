import { apiClient } from "@/lib/axios";

import type {
  RedeemRewardResult,
  RewardList,
} from "@/features/rewards/types/reward.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Recompensas — única camada autorizada a falar com
 * `apiClient` neste domínio. Hooks consomem estas funções; componentes nunca
 * importam `apiClient` diretamente.
 */
const REWARDS_ENDPOINT = "/api/v1/rewards";

export async function fetchRewards(): Promise<RewardList> {
  const { data } = await apiClient.get<ApiEnvelope<RewardList>>(REWARDS_ENDPOINT);
  return data.data;
}

export async function redeemReward(rewardId: string): Promise<RedeemRewardResult> {
  const { data } = await apiClient.post<ApiEnvelope<RedeemRewardResult>>(
    `${REWARDS_ENDPOINT}/${rewardId}/redeem`,
  );
  return data.data;
}
