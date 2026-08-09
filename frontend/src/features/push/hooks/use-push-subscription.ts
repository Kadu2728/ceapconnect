"use client";

import { useCallback, useEffect, useState } from "react";

import {
  fetchPushPublicKey,
  subscribePush,
  unsubscribePush,
} from "@/features/push/services/push.service";
import { urlBase64ToUint8Array } from "@/features/push/utils/vapid";

export type PushStatus =
  "loading" | "unsupported" | "not-configured" | "denied" | "subscribed" | "unsubscribed";

/**
 * Gerencia o ciclo de vida da inscrição de push do dispositivo atual: registra
 * o service worker, verifica o estado (suportado/permitido/inscrito) e expõe
 * `enable`/`disable` para o candidato ativar/desativar pelo Perfil ou pela
 * Central de Notificações.
 *
 * Nunca pede permissão automaticamente — só quando o candidato clica em
 * "Ativar", respeitando a decisão dele.
 */
export function usePushSubscription() {
  const [status, setStatus] = useState<PushStatus>("loading");
  const [isToggling, setIsToggling] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function init() {
      if (
        typeof window === "undefined" ||
        !("serviceWorker" in navigator) ||
        !("PushManager" in window)
      ) {
        setStatus("unsupported");
        return;
      }

      const keyResult = await fetchPushPublicKey();
      if (!keyResult.configured) {
        setStatus("not-configured");
        return;
      }
      if (Notification.permission === "denied") {
        setStatus("denied");
        return;
      }

      // O SW já é registrado app-wide em `AppProviders` (instalabilidade não
      // depende de push) — aqui só esperamos ele ficar pronto.
      const registration = await navigator.serviceWorker.ready;
      const existing = await registration.pushManager.getSubscription();
      if (!cancelled) setStatus(existing ? "subscribed" : "unsubscribed");
    }

    init().catch(() => {
      if (!cancelled) setStatus("unsupported");
    });

    return () => {
      cancelled = true;
    };
  }, []);

  const enable = useCallback(async () => {
    setIsToggling(true);
    try {
      const keyResult = await fetchPushPublicKey();
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setStatus("denied");
        return;
      }

      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(keyResult.public_key),
      });
      const json = subscription.toJSON();
      if (!json.endpoint || !json.keys?.p256dh || !json.keys?.auth) {
        throw new Error("Inscrição de push incompleta.");
      }

      await subscribePush({
        endpoint: json.endpoint,
        p256dh: json.keys.p256dh,
        auth: json.keys.auth,
      });
      setStatus("subscribed");
    } finally {
      setIsToggling(false);
    }
  }, []);

  const disable = useCallback(async () => {
    setIsToggling(true);
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        await unsubscribePush(subscription.endpoint);
        await subscription.unsubscribe();
      }
      setStatus("unsubscribed");
    } finally {
      setIsToggling(false);
    }
  }, []);

  return { status, isToggling, enable, disable };
}
