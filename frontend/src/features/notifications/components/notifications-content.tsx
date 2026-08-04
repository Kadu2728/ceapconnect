"use client";

import { motion, useReducedMotion } from "framer-motion";
import { BellOff, CheckCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { NotificationItem } from "@/features/notifications/components/notification-item";
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
} from "@/features/notifications/hooks/use-mark-notifications";
import type { NotificationList } from "@/features/notifications/types/notification.types";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface NotificationsContentProps {
  data: NotificationList;
}

/**
 * Composição da Central de Notificações: barra de resumo (não lidas + "marcar
 * todas") e a lista com entrada escalonada. Estado vazio acolhedor quando não
 * há nada — nunca uma tela morta.
 */
export function NotificationsContent({ data }: NotificationsContentProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();

  if (data.notifications.length === 0) {
    return (
      <Card className="items-center gap-3 py-16 text-center">
        <span className="flex size-14 items-center justify-center rounded-2xl bg-muted text-muted-foreground">
          <BellOff className="size-7" aria-hidden="true" />
        </span>
        <div className="px-6">
          <h3 className="font-semibold">Tudo em dia por aqui</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Você não tem notificações no momento. Avisos de eventos, missões e recompensas
            aparecem aqui.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          {data.unread_count > 0 ? (
            <>
              Você tem{" "}
              <span className="font-semibold text-foreground">{data.unread_count}</span>{" "}
              notificação(ões) não lida(s)
            </>
          ) : (
            "Nenhuma notificação não lida"
          )}
        </p>

        {data.unread_count > 0 ? (
          <Button
            variant="outline"
            size="sm"
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
          >
            <CheckCheck className="size-4" aria-hidden="true" />
            {markAllRead.isPending ? "Marcando…" : "Marcar todas como lidas"}
          </Button>
        ) : null}
      </div>

      <motion.ul
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="flex flex-col gap-2.5"
      >
        {data.notifications.map((notification) => (
          <motion.li key={notification.id} variants={itemVariants}>
            <NotificationItem
              notification={notification}
              onRead={(id) => markRead.mutate(id)}
            />
          </motion.li>
        ))}
      </motion.ul>
    </div>
  );
}
