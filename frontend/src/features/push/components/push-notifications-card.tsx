"use client";

import { Bell, BellOff, BellRing } from "lucide-react";

import { toast } from "@/components/feedback/toast/toast-store";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { usePushSubscription } from "@/features/push/hooks/use-push-subscription";

/**
 * Ativa/desativa notificações push do dispositivo atual (EPIC 18). Some da
 * tela quando o navegador não suporta push ou o servidor não tem push
 * configurado — nunca mostra uma ação que não vai funcionar.
 */
export function PushNotificationsCard() {
  const { status, isToggling, enable, disable } = usePushSubscription();

  if (status === "loading" || status === "unsupported" || status === "not-configured") {
    return null;
  }

  async function handleToggle() {
    try {
      if (status === "subscribed") {
        await disable();
        toast.success("Notificações desativadas neste dispositivo.");
      } else {
        await enable();
        toast.success("Notificações ativadas! Você vai receber avisos por aqui também.");
      }
    } catch {
      toast.error("Não foi possível atualizar as notificações push.", {
        description: "Tente novamente em instantes.",
      });
    }
  }

  return (
    <Card className="flex-row items-center gap-4 px-6 py-4">
      <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
        {status === "subscribed" ? (
          <BellRing className="size-5" aria-hidden="true" />
        ) : (
          <Bell className="size-5" aria-hidden="true" />
        )}
      </span>
      <div className="flex-1">
        <h3 className="text-sm font-semibold">Notificações no dispositivo</h3>
        <p className="text-sm text-muted-foreground">
          {status === "denied"
            ? "Bloqueadas nas permissões do navegador. Libere para ativar."
            : status === "subscribed"
              ? "Ativadas — você recebe avisos mesmo com o app fechado."
              : "Receba avisos de missões, eventos e recompensas na hora."}
        </p>
      </div>
      <Button
        variant={status === "subscribed" ? "outline" : "default"}
        size="sm"
        disabled={isToggling || status === "denied"}
        onClick={handleToggle}
      >
        {status === "subscribed" ? (
          <BellOff className="size-4" aria-hidden="true" />
        ) : (
          <Bell className="size-4" aria-hidden="true" />
        )}
        {isToggling ? "Aguarde…" : status === "subscribed" ? "Desativar" : "Ativar"}
      </Button>
    </Card>
  );
}
