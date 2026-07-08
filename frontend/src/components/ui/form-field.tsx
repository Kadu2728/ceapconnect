import type { ReactNode } from "react";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

interface FormFieldProps {
  /** Também usado para derivar os ids de erro/descrição (`${id}-error`, `${id}-description`) — devem bater com o `aria-describedby` do campo controlado. */
  id: string;
  label: string;
  error?: string;
  description?: string;
  required?: boolean;
  className?: string;
  children: ReactNode;
}

/**
 * Wrapper padrão de campo de formulário: label + controle + mensagem de
 * erro/descrição, com ids consistentes para `aria-describedby`.
 *
 * Reutilizável por qualquer feature (auth hoje; perfil, configurações etc.
 * mais adiante) — mantém toda tela do produto com a mesma hierarquia visual
 * de formulário (UI_UX_GUIDELINES.md: "boa hierarquia", "acessibilidade").
 */
export function FormField({
  id,
  label,
  error,
  description,
  required = false,
  className,
  children,
}: FormFieldProps) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <Label htmlFor={id}>
        {label}
        {required ? (
          <span aria-hidden="true" className="text-muted-foreground">
            *
          </span>
        ) : null}
      </Label>

      {children}

      {error ? (
        <p
          id={`${id}-error`}
          role="alert"
          className="text-xs font-medium text-destructive"
        >
          {error}
        </p>
      ) : description ? (
        <p id={`${id}-description`} className="text-xs text-muted-foreground">
          {description}
        </p>
      ) : null}
    </div>
  );
}
