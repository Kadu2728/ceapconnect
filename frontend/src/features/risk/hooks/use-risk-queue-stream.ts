"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { RISK_QUEUE_QUERY_KEY } from "@/features/risk/hooks/use-risk-queue";
import type { FetchRiskQueueParams } from "@/features/risk/services/risk.service";
import type { RiskQueueResponse } from "@/features/risk/types/risk.types";

const STREAM_PATH = "/api/v1/admin/risk/queue/stream";

/**
 * Mantém a fila de risco atualizada ao vivo (Fase 3 — moat), sem o
 * coordenador precisar dar F5. É um **complemento** a `useRiskQueue`, nunca
 * um substituto: usa `fetch` + leitura manual de stream (não a API
 * `EventSource`, que não permite header `Authorization`) e escreve
 * diretamente no cache do TanStack Query, na mesma chave que `useRiskQueue`
 * já usa — a UI não muda nada, só passa a receber updates sem pedir.
 *
 * Se o stream cair por qualquer motivo (rede, proxy, navegador antigo), a
 * experiência não quebra: `useRiskQueue` continua funcionando normalmente
 * com fetch comum, só sem os updates ao vivo.
 */
export function useRiskQueueStream(params: FetchRiskQueueParams = {}): {
  isLive: boolean;
} {
  const queryClient = useQueryClient();
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);
  const [isLive, setIsLive] = useState(false);

  const { cohortId, tier } = params;

  useEffect(() => {
    if (!hasHydrated || !accessToken) return;

    const controller = new AbortController();
    let cancelled = false;

    async function connect() {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const url = new URL(STREAM_PATH, apiUrl);
      if (cohortId) url.searchParams.set("cohort_id", cohortId);
      if (tier) url.searchParams.set("tier", tier);

      try {
        const res = await fetch(url.toString(), {
          headers: { Authorization: `Bearer ${accessToken}` },
          signal: controller.signal,
        });
        if (!res.ok || !res.body) return;

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (!cancelled) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          const events = buffer.split("\n\n");
          buffer = events.pop() ?? "";
          for (const event of events) {
            const dataLine = event.split("\n").find((line) => line.startsWith("data: "));
            if (!dataLine) continue; // heartbeat (": ...") ou chunk incompleto
            try {
              const data = JSON.parse(
                dataLine.slice("data: ".length),
              ) as RiskQueueResponse;
              // Reconstruído a partir de cohortId/tier (não do `params` do
              // parâmetro) para casar exatamente com as dependências do
              // efeito abaixo — mesmo objeto que `useRiskQueue` monta como
              // chave, então o cache é atualizado na entrada certa.
              queryClient.setQueryData(
                [...RISK_QUEUE_QUERY_KEY, { cohortId, tier }],
                data,
              );
              setIsLive(true);
            } catch {
              // Chunk malformado — ignora e segue lendo o stream.
            }
          }
        }
      } catch {
        // Conexão perdida/abortada — sem retry agressivo, useRiskQueue
        // cobre a experiência via fetch normal.
      } finally {
        if (!cancelled) setIsLive(false);
      }
    }

    void connect();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [hasHydrated, accessToken, cohortId, tier, queryClient]);

  return { isLive };
}
