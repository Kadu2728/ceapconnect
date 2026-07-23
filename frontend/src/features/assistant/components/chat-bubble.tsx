import type { ChatRole } from "@/features/assistant/types/assistant.types";
import { cn } from "@/lib/utils";

function TypingDots() {
  return (
    <span className="inline-flex items-center gap-1 py-1" aria-label="Digitando…">
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          className="size-1.5 animate-bounce rounded-full bg-muted-foreground/60"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </span>
  );
}

interface ChatBubbleProps {
  role: ChatRole;
  content: string;
}

/**
 * Bolha de uma mensagem do chat. Usuário à direita (cor de marca), assistente
 * à esquerda (neutro). Enquanto a resposta do assistente ainda não chegou,
 * mostra um indicador de digitação.
 */
export function ChatBubble({ role, content }: ChatBubbleProps) {
  const isUser = role === "user";

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-3.5 py-2 text-sm break-words whitespace-pre-wrap",
          isUser
            ? "rounded-br-sm bg-brand text-brand-foreground"
            : "rounded-bl-sm bg-muted text-foreground",
        )}
      >
        {content === "" ? <TypingDots /> : content}
      </div>
    </div>
  );
}
