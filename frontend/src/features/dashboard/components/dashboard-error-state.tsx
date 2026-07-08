import { AlertTriangle, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";

interface DashboardErrorStateProps {
  onRetry: () => void;
}

/**
 * Estado de erro do Dashboard — nunca uma tela crua (UI_UX_GUIDELINES.md).
 * A sessão continua válida; apenas a chamada de dados falhou, então
 * oferecemos uma ação clara de recuperação em vez de deslogar o candidato.
 */
export function DashboardErrorState({ onRetry }: DashboardErrorStateProps) {
  return (
    <div className="flex w-full max-w-md flex-col items-center gap-4 rounded-2xl border bg-card px-6 py-10 text-center shadow-sm">
      <span className="flex size-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
        <AlertTriangle className="size-6" aria-hidden="true" />
      </span>

      <div className="flex flex-col gap-1.5">
        <h1 className="text-xl font-semibold tracking-tight">
          Não foi possível carregar seu Dashboard
        </h1>
        <p className="text-sm text-muted-foreground">
          Verifique sua conexão e tente novamente. Sua sessão continua ativa.
        </p>
      </div>

      <Button onClick={onRetry} className="mt-2 gap-2">
        <RotateCcw className="size-4" aria-hidden="true" />
        Tentar novamente
      </Button>
    </div>
  );
}
