import { apiClient } from "@/lib/axios";

import type { PushPublicKey, PushSubscribeInput } from "@/features/push/types/push.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service de Push Notifications — única camada autorizada a falar com
 * `apiClient` neste domínio.
 */
const PUSH_ENDPOINT = "/api/v1/push";

export async function fetchPushPublicKey(): Promise<PushPublicKey> {
  const { data } = await apiClient.get<ApiEnvelope<PushPublicKey>>(
    `${PUSH_ENDPOINT}/public-key`,
  );
  return data.data;
}

export async function subscribePush(input: PushSubscribeInput): Promise<void> {
  await apiClient.post(`${PUSH_ENDPOINT}/subscribe`, input);
}

export async function unsubscribePush(endpoint: string): Promise<void> {
  await apiClient.post(`${PUSH_ENDPOINT}/unsubscribe`, { endpoint });
}
