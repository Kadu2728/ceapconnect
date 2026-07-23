"use client";

import { useCallback, useRef, useState } from "react";

import { streamAssistantReply } from "@/features/assistant/services/assistant.service";
import type { ChatMessage, ChatRole } from "@/features/assistant/types/assistant.types";

export interface UiMessage {
  id: string;
  role: ChatRole;
  content: string;
}

const STREAM_ERROR_MESSAGE = "Desculpe, não consegui responder agora. Tente novamente.";

/**
 * Estado local do chat com o assistente: mensagens, streaming em andamento e a
 * ação de enviar. A resposta chega token a token e é anexada à última mensagem
 * do assistente conforme streama.
 */
export function useAssistantChat() {
  const [messages, setMessages] = useState<UiMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const seededRef = useRef(false);

  const seed = useCallback((history: ChatMessage[]) => {
    if (seededRef.current) return;
    seededRef.current = true;
    setMessages(
      history.map((message) => ({
        id: message.id,
        role: message.role,
        content: message.content,
      })),
    );
  }, []);

  const send = useCallback(async (text: string) => {
    const userId = crypto.randomUUID();
    const assistantId = crypto.randomUUID();

    setMessages((prev) => [
      ...prev,
      { id: userId, role: "user", content: text },
      { id: assistantId, role: "assistant", content: "" },
    ]);
    setIsStreaming(true);

    try {
      await streamAssistantReply(text, (chunk) => {
        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? { ...message, content: message.content + chunk }
              : message,
          ),
        );
      });
    } catch {
      setMessages((prev) =>
        prev.map((message) =>
          message.id === assistantId && message.content === ""
            ? { ...message, content: STREAM_ERROR_MESSAGE }
            : message,
        ),
      );
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return { messages, isStreaming, send, seed };
}
