import { apiClient } from "@/lib/axios";

import type {
  AdminOverview,
  AdminRedemption,
  AdminRedemptionList,
  AdminReward,
  AdminRewardInput,
  AdminRewardList,
} from "@/features/admin/types/admin.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Admin — única camada autorizada a falar com `apiClient`
 * neste domínio.
 */
const ADMIN_OVERVIEW_ENDPOINT = "/api/v1/admin/overview";
const ADMIN_REDEMPTIONS_ENDPOINT = "/api/v1/admin/redemptions";
const ADMIN_REWARDS_ENDPOINT = "/api/v1/admin/rewards";

export async function fetchAdminOverview(): Promise<AdminOverview> {
  const { data } = await apiClient.get<ApiEnvelope<AdminOverview>>(
    ADMIN_OVERVIEW_ENDPOINT,
  );
  return data.data;
}

export async function fetchRedemptions(): Promise<AdminRedemptionList> {
  const { data } = await apiClient.get<ApiEnvelope<AdminRedemptionList>>(
    ADMIN_REDEMPTIONS_ENDPOINT,
  );
  return data.data;
}

export async function fulfillRedemption(redemptionId: string): Promise<AdminRedemption> {
  const { data } = await apiClient.post<ApiEnvelope<AdminRedemption>>(
    `${ADMIN_REDEMPTIONS_ENDPOINT}/${redemptionId}/fulfill`,
  );
  return data.data;
}

export async function fetchAdminRewards(): Promise<AdminRewardList> {
  const { data } =
    await apiClient.get<ApiEnvelope<AdminRewardList>>(ADMIN_REWARDS_ENDPOINT);
  return data.data;
}

export async function createReward(input: AdminRewardInput): Promise<AdminReward> {
  const { data } = await apiClient.post<ApiEnvelope<AdminReward>>(
    ADMIN_REWARDS_ENDPOINT,
    input,
  );
  return data.data;
}

export async function updateReward(
  rewardId: string,
  input: AdminRewardInput,
): Promise<AdminReward> {
  const { data } = await apiClient.patch<ApiEnvelope<AdminReward>>(
    `${ADMIN_REWARDS_ENDPOINT}/${rewardId}`,
    input,
  );
  return data.data;
}
