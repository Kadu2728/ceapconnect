"use client";

import { Check } from "lucide-react";
import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Checkbox estilizado sobre um `<input type="checkbox">` nativo (não usa
 * `@radix-ui/react-checkbox`, não instalado no projeto). O input real fica
 * visível para leitores de tela e navegação por teclado; o quadrado
 * customizado e o ícone de check são puramente visuais (`aria-hidden`),
 * garantindo o mesmo comportamento de acessibilidade de um checkbox nativo
 * sem dependências extras.
 */
const Checkbox = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, ...props }, ref) => {
    return (
      <span className="relative inline-flex size-5 shrink-0">
        <input
          type="checkbox"
          ref={ref}
          data-slot="checkbox"
          className={cn(
            "peer size-5 shrink-0 cursor-pointer appearance-none rounded-[4px] border border-input bg-transparent shadow-xs outline-none transition-colors",
            "checked:border-primary checked:bg-primary",
            "focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50",
            "disabled:cursor-not-allowed disabled:opacity-50",
            "aria-invalid:border-destructive aria-invalid:ring-destructive/20",
            className,
          )}
          {...props}
        />
        <Check
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 m-auto size-3.5 text-primary-foreground opacity-0 peer-checked:opacity-100"
        />
      </span>
    );
  },
);
Checkbox.displayName = "Checkbox";

export { Checkbox };
