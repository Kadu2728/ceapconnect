import { createElement } from "react";

import type { Notification } from "@/features/notifications/types/notification.types";
import { resolveNotificationCategory } from "@/features/notifications/utils/notification-category";
import { cn } from "@/lib/utils";

const RELATIVE = new Intl.RelativeTimeFormat("pt-BR", { numeric: "auto" });
const ABSOLUTE = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

/** Tempo relativo curto ("há 5 min", "há 2 h") ou data absoluta se > 7 dias. */
function formatWhen(iso: string): string {
  const date = new Date(iso);
  const diffMs = date.getTime() - Date.now();
  const diffMin = Math.round(diffMs / 60000);

  if (Math.abs(diffMin) < 60) return RELATIVE.format(diffMin, "minute");
  const diffHours = Math.round(diffMin / 60);
  if (Math.abs(diffHours) < 24) return RELATIVE.format(diffHours, "hour");
  const diffDays = Math.round(diffHours / 24);
  if (Math.abs(diffDays) <= 7) return RELATIVE.format(diffDays, "day");
  return ABSOLUTE.format(date);
}

interface NotificationItemProps {
  notification: Notification;
  onRead: (id: string) => void;
}

/**
 * Item da central de notificações. Não lida: fundo suave de marca + ponto de
 * destaque; ao clicar/focar, marca como lida. Lida: estado calmo. Acessível via
 * teclado (é um `<button>` de largura total).
 */
export function NotificationItem({ notification, onRead }: NotificationItemProps) {
  const { icon, tone, label } = resolveNotificationCategory(notification.category);
  const isUnread = !notification.read;

  return (
    <button
      type="button"
      onClick={() => isUnread && onRead(notification.id)}
      aria-label={
        isUnread
          ? `${notification.title} (não lida) — marcar como lida`
          : notification.title
      }
      className={cn(
        "flex w-full items-start gap-3 rounded-xl border px-4 py-3.5 text-left transition-colors",
        isUnread
          ? "border-brand/20 bg-brand/[0.04] hover:bg-brand/[0.07]"
          : "border-border/60 hover:bg-accent/50",
      )}
    >
      <span
        className={cn(
          "flex size-10 shrink-0 items-center justify-center rounded-xl",
          tone,
        )}
      >
        {createElement(icon, { className: "size-5", "aria-hidden": true })}
      </span>

      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <p
            className={cn("truncate text-sm", isUnread ? "font-semibold" : "font-medium")}
          >
            {notification.title}
          </p>
          {isUnread ? (
            <span aria-hidden="true" className="size-2 shrink-0 rounded-full bg-brand" />
          ) : null}
        </div>
        <p className="mt-0.5 text-sm text-muted-foreground">{notification.description}</p>
        <p className="mt-1 text-xs text-muted-foreground">
          {label} · {formatWhen(notification.created_at)}
        </p>
      </div>
    </button>
  );
}
