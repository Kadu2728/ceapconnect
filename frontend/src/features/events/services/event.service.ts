import { apiClient } from "@/lib/axios";

import type {
  EventList,
  EventRegistrationResult,
} from "@/features/events/types/event.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Eventos — única camada autorizada a falar com `apiClient`
 * neste domínio.
 */
const EVENTS_ENDPOINT = "/api/v1/events";

export async function fetchEvents(): Promise<EventList> {
  const { data } = await apiClient.get<ApiEnvelope<EventList>>(EVENTS_ENDPOINT);
  return data.data;
}

export async function registerEvent(eventId: string): Promise<EventRegistrationResult> {
  const { data } = await apiClient.post<ApiEnvelope<EventRegistrationResult>>(
    `${EVENTS_ENDPOINT}/${eventId}/register`,
  );
  return data.data;
}

export async function cancelEventRegistration(
  eventId: string,
): Promise<EventRegistrationResult> {
  const { data } = await apiClient.delete<ApiEnvelope<EventRegistrationResult>>(
    `${EVENTS_ENDPOINT}/${eventId}/register`,
  );
  return data.data;
}
