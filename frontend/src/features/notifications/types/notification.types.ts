/**
 * Contratos da Central de Notificações (EPIC 08), espelhando o backend
 * (`/api/v1/notifications`). Campos em `snake_case` como o backend os envia.
 */

export type NotificationCategory =
  "sistema" | "eventos" | "missoes" | "lembretes" | "resultado";

export interface Notification {
  id: string;
  title: string;
  description: string;
  category: NotificationCategory;
  read: boolean;
  created_at: string;
}

export interface NotificationList {
  notifications: Notification[];
  unread_count: number;
}

export interface MarkAllReadResult {
  marked: number;
  unread_count: number;
}
