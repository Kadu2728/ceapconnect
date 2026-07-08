import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Label acessível para campos de formulário.
 *
 * Implementado sem `@radix-ui/react-label` (não instalado no projeto) — não
 * há ganho real aqui além do que a tag `<label>` nativa já oferece, já que
 * não usamos o contexto de `Form` do Radix.
 */
function Label({ className, ...props }: React.ComponentProps<"label">) {
  return (
    <label
      data-slot="label"
      className={cn(
        "flex select-none items-center gap-1.5 text-sm leading-none font-medium",
        "peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}

export { Label };
