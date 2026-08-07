import type { RiskTier } from "@/features/risk/types/risk.types";
import { resolveTierStyle } from "@/features/risk/utils/risk-tone";
import { cn } from "@/lib/utils";

interface RiskBadgeProps {
  score: number;
  tier: RiskTier;
  className?: string;
}

/**
 * Pill compacto de score + tier (ex.: "80 · Alto risco"), colorido por
 * severidade. É o primeiro sinal visual que o coordenador vê ao escanear a
 * fila — precisa ser lido em menos de 1 segundo.
 */
export function RiskBadge({ score, tier, className }: RiskBadgeProps) {
  const { label, tone } = resolveTierStyle(tier);

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold",
        tone,
        className,
      )}
    >
      <span className="tabular-nums">{score}</span>
      <span aria-hidden="true">·</span>
      {label}
    </span>
  );
}
