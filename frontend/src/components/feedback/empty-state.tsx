import type { LucideIcon } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface EmptyStateAction {
  label: string;
  href: string;
}

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: EmptyStateAction;
  /**
   * Nível semântico do heading do título. Use `"h1"` quando o EmptyState for
   * o conteúdo principal da página (garante um único `h1` por rota); use o
   * padrão `"h2"` quando estiver aninhado em uma página que já possui h1
   * (ex.: uma lista vazia dentro do Dashboard).
   */
  headingLevel?: "h1" | "h2";
  className?: string;
}

/**
 * Estado vazio/placeholder reutilizável (DESIGN_SYSTEM.md → "Empty State").
 *
 * Usado sempre que um fluxo ainda não está disponível ou não há dados para
 * exibir — nenhuma tela do produto deve ficar sem contexto ou feedback
 * (UI_UX_GUIDELINES.md: "todo fluxo deve terminar com feedback positivo").
 */
export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  headingLevel = "h2",
  className,
}: EmptyStateProps) {
  const Heading = headingLevel;

  return (
    <div
      className={cn(
        "flex w-full max-w-md flex-col items-center gap-4 rounded-2xl border bg-card px-6 py-10 text-center shadow-sm",
        className,
      )}
    >
      <span className="flex size-12 items-center justify-center rounded-full bg-accent text-accent-foreground">
        <Icon className="size-6" aria-hidden="true" />
      </span>

      <div className="flex flex-col gap-1.5">
        <Heading className="text-xl font-semibold tracking-tight">{title}</Heading>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>

      {action ? (
        <Button asChild className="mt-2">
          <Link href={action.href}>{action.label}</Link>
        </Button>
      ) : null}
    </div>
  );
}
