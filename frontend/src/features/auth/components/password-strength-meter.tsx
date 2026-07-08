import { getPasswordStrength } from "@/features/auth/utils/password-strength";
import { cn } from "@/lib/utils";

interface PasswordStrengthMeterProps {
  password: string;
}

const STRENGTH_CONFIG = {
  fraca: { label: "Fraca", barClassName: "w-1/3 bg-destructive" },
  média: { label: "Média", barClassName: "w-2/3 bg-warning" },
  forte: { label: "Forte", barClassName: "w-full bg-success" },
} as const;

/**
 * Indicador visual de força de senha — feedback imediato que incentiva
 * senhas melhores sem bloquear o envio (a única regra obrigatória é o
 * mínimo de 8 caracteres, validado via Zod e espelhando o backend).
 */
export function PasswordStrengthMeter({ password }: PasswordStrengthMeterProps) {
  const strength = getPasswordStrength(password);

  if (!strength) return null;

  const config = STRENGTH_CONFIG[strength];

  return (
    <div className="flex items-center gap-2" aria-live="polite">
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-200",
            config.barClassName,
          )}
        />
      </div>
      <span className="text-xs whitespace-nowrap text-muted-foreground">
        {config.label}
      </span>
    </div>
  );
}
