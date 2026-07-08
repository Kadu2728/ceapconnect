import { Zap } from "lucide-react";

interface XpBadgeProps {
  xpTotal: number;
}

/**
 * Indicador de XP total do candidato, estilo "pill" — visível logo ao lado
 * da saudação, reforçando progresso sem competir visualmente com o título
 * (DESIGN_SYSTEM.md: cor de destaque única, `accent`).
 */
export function XpBadge({ xpTotal }: XpBadgeProps) {
  return (
    <span className="inline-flex w-fit items-center gap-1.5 rounded-full bg-accent px-3.5 py-1.5 text-sm font-semibold text-accent-foreground">
      <Zap className="size-4" aria-hidden="true" />
      {xpTotal.toLocaleString("pt-BR")} XP
    </span>
  );
}
