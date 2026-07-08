import type { LucideIcon } from "lucide-react";

interface InlineEmptyStateProps {
  icon: LucideIcon;
  message: string;
}

/**
 * Estado vazio leve para listas aninhadas dentro de um card do Dashboard
 * (conquistas, eventos). O `EmptyState` padrão (`components/feedback`) é
 * pensado para ocupar a página inteira — empilhar dois cartões visuais
 * dentro de um só ficaria pesado; este é um slot mais discreto, com o mesmo
 * espírito (ícone + mensagem clara), para caber dentro de outro card.
 */
export function InlineEmptyState({ icon: Icon, message }: InlineEmptyStateProps) {
  return (
    <div className="mt-5 flex flex-col items-center gap-2 rounded-xl border border-dashed py-8 text-center">
      <Icon className="size-6 text-muted-foreground" aria-hidden="true" />
      <p className="max-w-xs text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
