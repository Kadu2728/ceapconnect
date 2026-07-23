"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Send, Sparkles, X } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { ChatBubble } from "@/features/assistant/components/chat-bubble";
import { useAssistantChat } from "@/features/assistant/hooks/use-assistant-chat";
import { useAssistantHistory } from "@/features/assistant/hooks/use-assistant-history";
import { cn } from "@/lib/utils";

const SUGGESTIONS = [
  "Como funciona o processo seletivo?",
  "Quais cursos o CEAP oferece?",
  "Como eu ganho XP nas missões?",
];

/**
 * Assistente de IA do CEAP Connect: bolha flutuante que abre um chat com
 * respostas em streaming. Disponível em toda a área autenticada (montado na
 * `AuthenticatedShell`). Carrega o histórico ao abrir e faz auto-scroll.
 */
export function AssistantWidget() {
  const shouldReduceMotion = useReducedMotion();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");

  const historyQuery = useAssistantHistory(open);
  const { messages, isStreaming, send, seed } = useAssistantChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (historyQuery.data) {
      seed(historyQuery.data.messages);
    }
  }, [historyQuery.data, seed]);

  useEffect(() => {
    const node = scrollRef.current;
    if (node) node.scrollTo({ top: node.scrollHeight });
  }, [messages, open]);

  const submit = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;
    setInput("");
    void send(trimmed);
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    submit(input);
  };

  const isEmpty = messages.length === 0 && !historyQuery.isPending;

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-label={open ? "Fechar assistente" : "Abrir assistente"}
        aria-expanded={open}
        className={cn(
          "fixed right-4 bottom-20 z-50 flex size-14 items-center justify-center rounded-full",
          "bg-gradient-to-br from-brand to-brand-2 text-brand-foreground shadow-lg shadow-brand/30",
          "transition-transform hover:scale-105 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none",
          "md:right-6 md:bottom-6",
        )}
      >
        {open ? <X className="size-6" /> : <Sparkles className="size-6" />}
      </button>

      <AnimatePresence>
        {open ? (
          <motion.div
            role="dialog"
            aria-label="Assistente CEAP"
            initial={{
              opacity: 0,
              y: shouldReduceMotion ? 0 : 16,
              scale: shouldReduceMotion ? 1 : 0.98,
            }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{
              opacity: 0,
              y: shouldReduceMotion ? 0 : 16,
              scale: shouldReduceMotion ? 1 : 0.98,
            }}
            transition={{ duration: shouldReduceMotion ? 0 : 0.2, ease: "easeOut" }}
            className={cn(
              "fixed inset-x-3 top-16 bottom-3 z-50 flex flex-col overflow-hidden rounded-2xl border border-border/70 bg-card shadow-2xl",
              "md:inset-x-auto md:top-auto md:right-6 md:bottom-24 md:h-[560px] md:max-h-[80vh] md:w-96",
            )}
          >
            {/* Header */}
            <div className="flex items-center gap-3 border-b border-border/60 bg-gradient-to-r from-brand to-brand-2 px-4 py-3 text-brand-foreground">
              <span className="flex size-9 items-center justify-center rounded-full bg-white/20">
                <Sparkles className="size-5" aria-hidden="true" />
              </span>
              <div className="flex-1">
                <p className="text-sm font-semibold">Assistente CEAP</p>
                <p className="text-xs text-brand-foreground/80">
                  Tire suas dúvidas sobre o CEAP
                </p>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Fechar"
                className="rounded-md p-1 transition-colors hover:bg-white/15"
              >
                <X className="size-5" />
              </button>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
              {isEmpty ? (
                <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
                  <span className="flex size-12 items-center justify-center rounded-2xl bg-brand/10 text-brand">
                    <Sparkles className="size-6" aria-hidden="true" />
                  </span>
                  <div>
                    <p className="font-semibold text-foreground">
                      Olá! Como posso ajudar?
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Pergunte sobre o processo seletivo, os cursos ou como usar o app.
                    </p>
                  </div>
                  <div className="flex flex-col gap-2">
                    {SUGGESTIONS.map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        onClick={() => submit(suggestion)}
                        className="rounded-full border border-border/70 px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:border-brand/40 hover:text-foreground"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <ChatBubble
                    key={message.id}
                    role={message.role}
                    content={message.content}
                  />
                ))
              )}
            </div>

            {/* Input */}
            <form
              onSubmit={handleSubmit}
              className="flex items-center gap-2 border-t border-border/60 p-3"
            >
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Escreva sua pergunta…"
                aria-label="Sua pergunta"
                disabled={isStreaming}
                className="h-10 flex-1 rounded-full border border-input bg-background px-4 text-sm outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:opacity-60"
              />
              <Button
                type="submit"
                size="icon"
                disabled={isStreaming || input.trim() === ""}
                aria-label="Enviar"
                className="size-10 shrink-0 rounded-full"
              >
                <Send className="size-4" />
              </Button>
            </form>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </>
  );
}
