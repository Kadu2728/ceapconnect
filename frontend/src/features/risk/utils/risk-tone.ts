import type { RiskTier } from "@/features/risk/types/risk.types";

interface TierStyle {
  label: string;
  /** Classes de cor do badge/tile (fundo suave + texto). */
  tone: string;
  /** Cor sólida (para barras/indicadores pequenos). */
  dot: string;
}

/**
 * Mapa de tier → cor e rótulo. Vermelho/laranja/verde é a leitura mais rápida
 * possível para um coordenador triando uma fila — não é decorativo.
 */
const TIER_STYLES: Record<RiskTier, TierStyle> = {
  alto: {
    label: "Alto risco",
    tone: "bg-destructive/10 text-destructive",
    dot: "bg-destructive",
  },
  medio: {
    label: "Risco médio",
    tone: "bg-brand-orange/10 text-brand-orange",
    dot: "bg-brand-orange",
  },
  baixo: { label: "Baixo risco", tone: "bg-success/10 text-success", dot: "bg-success" },
};

export function resolveTierStyle(tier: RiskTier): TierStyle {
  return TIER_STYLES[tier];
}
