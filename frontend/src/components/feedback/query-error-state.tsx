import { AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";

interface QueryErrorStateProps {
  onRetry: () => void;
  title?: string;
  description?: string;
}

/**
 * Estado de erro genérico para páginas apoiadas em uma query, com ação clara de
 * recuperação (`error-recovery`). Reutilizado por Missões, Conquistas e Eventos.
 */
export function QueryErrorState({
  onRetry,
  title = "Não foi possível carregar",
  description = "Ocorreu um erro ao buscar os dados. Verifique sua conexão e tente novamente.",
}: QueryErrorStateProps) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 text-center">
      <span className="flex size-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
        <AlertCircle className="size-6" aria-hidden="true" />
      </span>
      <div>
        <h2 className="font-semibold">{title}</h2>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>
      </div>
      <Button variant="outline" onClick={onRetry}>
        Tentar novamente
      </Button>
    </div>
  );
}
