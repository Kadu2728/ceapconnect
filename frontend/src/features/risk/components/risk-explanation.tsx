import { Info } from "lucide-react";

import type { RiskFactor } from "@/features/risk/types/risk.types";

interface RiskExplanationProps {
  /** Texto pronto do backend (ex.: "Sem atividade há 5 dias · Travado em..."). */
  explanation: string;
}

interface RiskExplanationDetailedProps {
  /** Decomposição completa dos fatores, com o peso de cada um (tela de detalhe). */
  factors: RiskFactor[];
}

/** Versão compacta: quebra a string do backend em chips, para a fila/lista. */
export function RiskExplanation({ explanation }: RiskExplanationProps) {
  const reasons = explanation
    .split("·")
    .map((reason) => reason.trim())
    .filter(Boolean);

  if (reasons.length === 0) {
    return <p className="text-sm text-muted-foreground">{explanation}</p>;
  }

  return (
    <ul className="flex flex-wrap gap-1.5">
      {reasons.map((reason) => (
        <li
          key={reason}
          className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground"
        >
          {reason}
        </li>
      ))}
    </ul>
  );
}

/** Versão detalhada: cada fator com o peso exato no score, para a gaveta de intervenção. */
export function RiskExplanationDetailed({ factors }: RiskExplanationDetailedProps) {
  const contributing = factors
    .filter((factor) => factor.points > 0)
    .sort((a, b) => b.points - a.points);

  if (contributing.length === 0) {
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <Info className="size-4 shrink-0" aria-hidden="true" />
        Nenhum sinal de risco identificado.
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {contributing.map((factor) => (
        <li key={factor.key} className="flex items-center justify-between gap-3 text-sm">
          <span>{factor.label}</span>
          <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs font-semibold tabular-nums text-muted-foreground">
            +{Math.round(factor.points)}
          </span>
        </li>
      ))}
    </ul>
  );
}
