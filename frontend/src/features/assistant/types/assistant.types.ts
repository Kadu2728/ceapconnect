/**
 * Contratos da feature Assistente IA (EPIC 11).
 *
 * O `POST /chat` responde em streaming de texto puro (consumido via `fetch` +
 * `ReadableStream`), por isso não há tipo de resposta aqui — só o histórico.
 */

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  created_at: string;
}

export interface ChatHistory {
  messages: ChatMessage[];
  /** Indica se a chave da IA está configurada no backend. */
  configured: boolean;
}
