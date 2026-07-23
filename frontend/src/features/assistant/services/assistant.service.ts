import { useAuthStore } from "@/features/auth/store/auth-store";
import { apiClient } from "@/lib/axios";

import type { ChatHistory } from "@/features/assistant/types/assistant.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Assistente IA.
 *
 * O histórico usa o `apiClient` (axios) padrão. Já o chat é *streaming*: usamos
 * `fetch` nativo com `ReadableStream` porque o axios no browser não expõe o
 * corpo em pedaços — o token é injetado manualmente a partir da store de auth.
 */
const ASSISTANT_BASE = "/api/v1/assistant";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchAssistantHistory(): Promise<ChatHistory> {
  const { data } = await apiClient.get<ApiEnvelope<ChatHistory>>(
    `${ASSISTANT_BASE}/history`,
  );
  return data.data;
}

/**
 * Envia uma mensagem e transmite a resposta do assistente token a token via
 * `onToken`. Retorna o texto completo ao final. Aborta via `signal`.
 */
export async function streamAssistantReply(
  message: string,
  onToken: (chunk: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  const accessToken = useAuthStore.getState().accessToken;

  const response = await fetch(`${API_BASE_URL}${ASSISTANT_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!response.ok || response.body === null) {
    throw new Error("Falha ao obter a resposta do assistente.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let full = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    if (chunk) {
      full += chunk;
      onToken(chunk);
    }
  }

  return full;
}
