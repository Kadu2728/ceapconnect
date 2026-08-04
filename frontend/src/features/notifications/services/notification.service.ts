import { apiClient } from "@/lib/axios";

import type {
  MarkAllReadResult,
  Notification,
  NotificationList,
} from "@/features/notifications/types/notification.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da Central de Notificações — única camada autorizada a falar com
 * `apiClient` neste domínio.
 */
const NOTIFICATIONS_ENDPOINT = "/api/v1/notifications";

export async function fetchNotifications(): Promise<NotificationList> {
  const { data } =
    await apiClient.get<ApiEnvelope<NotificationList>>(NOTIFICATIONS_ENDPOINT);
  return data.data;
}

export async function markNotificationRead(
  notificationId: string,
): Promise<Notification> {
  const { data } = await apiClient.post<ApiEnvelope<Notification>>(
    `${NOTIFICATIONS_ENDPOINT}/${notificationId}/read`,
  );
  return data.data;
}

export async function markAllNotificationsRead(): Promise<MarkAllReadResult> {
  const { data } = await apiClient.post<ApiEnvelope<MarkAllReadResult>>(
    `${NOTIFICATIONS_ENDPOINT}/read-all`,
  );
  return data.data;
}
