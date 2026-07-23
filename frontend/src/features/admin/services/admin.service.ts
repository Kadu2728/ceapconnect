import { apiClient } from "@/lib/axios";

import type {
  AdminOverview,
  AdminRedemption,
  AdminRedemptionList,
} from "@/features/admin/types/admin.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Admin — única camada autorizada a falar com `apiClient`
 * neste domínio.
 */
const ADMIN_OVERVIEW_ENDPOINT = "/api/v1/admin/overview";
const ADMIN_REDEMPTIONS_ENDPOINT = "/api/v1/admin/redemptions";

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
