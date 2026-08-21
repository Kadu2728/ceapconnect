"use client";

import { motion, useReducedMotion } from "framer-motion";
import { CheckCircle2, ChevronRight, Users } from "lucide-react";
import { useState } from "react";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { Card } from "@/components/ui/card";
import { RiskBadge } from "@/features/risk/components/risk-badge";
import { RiskExplanation } from "@/features/risk/components/risk-explanation";
import { useRiskQueue } from "@/features/risk/hooks/use-risk-queue";
import { useRiskQueueStream } from "@/features/risk/hooks/use-risk-queue-stream";
import type { RiskQueueItem, RiskTier } from "@/features/risk/types/risk.types";
import { resolveTierStyle } from "@/features/risk/utils/risk-tone";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";
import { cn } from "@/lib/utils";

const TIER_FILTERS: { value: RiskTier | undefined; label: string }[] = [
  { value: undefined, label: "Todos" },
  { value: "alto", label: "Alto" },
  { value: "medio", label: "Médio" },
  { value: "baixo", label: "Baixo" },
];

interface RiskQueueProps {
  onSelectCandidate: (candidateProfileId: string) => void;
}

/**
 * Fila priorizada de risco: resumo por tier + filtro + lista ordenada do
 * candidato mais arriscado para o menos, cada card já mostra o "porquê" em
 * linguagem humana (nunca só o número). Clicar num card abre a gaveta de
 * intervenção.
 */
export function RiskQueue({ onSelectCandidate }: RiskQueueProps) {
  const [tier, setTier] = useState<RiskTier | undefined>(undefined);
  const query = useRiskQueue({ tier });
  const { isLive } = useRiskQueueStream({ tier });

  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  if (query.isPending) {
    return <CardListSkeleton count={5} withSummary />;
  }
  if (!query.isSuccess) {
    return <QueryErrorState onRetry={() => query.refetch()} />;
  }

  const { items, total, counts_by_tier: countsByTier } = query.data;

  return (
    <div className="flex flex-col gap-4">
      <Card className="gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3 px-6">
          <div className="flex items-center gap-2">
            <Users className="size-5 text-brand" aria-hidden="true" />
            <div>
              <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
                Candidatos monitorados
                {isLive ? (
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-success">
                    <span className="relative flex size-1.5">
                      {shouldReduceMotion ? null : (
                        <span className="absolute inline-flex size-full animate-ping rounded-full bg-success opacity-75" />
                      )}
                      <span className="relative inline-flex size-1.5 rounded-full bg-success" />
                    </span>
                    ao vivo
                  </span>
                ) : null}
              </p>
              <p className="text-2xl font-bold tracking-tight tabular-nums">{total}</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {(["alto", "medio", "baixo"] as const).map((tierKey) => {
              const { label, tone } = resolveTierStyle(tierKey);
              return (
                <span
                  key={tierKey}
                  className={cn(
                    "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold",
                    tone,
                  )}
                >
                  {countsByTier[tierKey] ?? 0} · {label}
                </span>
              );
            })}
          </div>
        </div>

        <div className="flex flex-wrap gap-2 px-6">
          {TIER_FILTERS.map((filter) => (
            <button
              key={filter.label}
              type="button"
              aria-pressed={tier === filter.value}
              onClick={() => setTier(filter.value)}
              className={cn(
                "rounded-md border px-3 py-1.5 text-sm font-medium transition-colors",
                tier === filter.value
                  ? "border-brand bg-brand/10 text-brand"
                  : "border-input text-muted-foreground hover:bg-accent/50",
              )}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </Card>

      {items.length === 0 ? (
        <Card className="items-center gap-3 py-16 text-center">
          <span className="flex size-14 items-center justify-center rounded-2xl bg-success/10 text-success">
            <CheckCircle2 className="size-7" aria-hidden="true" />
          </span>
          <div className="px-6">
            <h3 className="font-semibold">Nenhum candidato nesta faixa</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Ninguém em risco por aqui no momento — bom sinal.
            </p>
          </div>
        </Card>
      ) : (
        <motion.ul
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="flex flex-col gap-3"
        >
          {items.map((item) => (
            <motion.li key={item.candidate_profile_id} variants={itemVariants}>
              <QueueRow
                item={item}
                onClick={() => onSelectCandidate(item.candidate_profile_id)}
              />
            </motion.li>
          ))}
        </motion.ul>
      )}
    </div>
  );
}

function QueueRow({ item, onClick }: { item: RiskQueueItem; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center gap-4 rounded-xl border bg-card px-5 py-4 text-left transition-all hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-md"
    >
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="font-medium">{item.candidate_name}</p>
          {item.cohort_name ? (
            <span className="text-xs text-muted-foreground">{item.cohort_name}</span>
          ) : null}
        </div>
        <div className="mt-1.5">
          <RiskExplanation explanation={item.explanation} />
        </div>
      </div>

      <RiskBadge score={item.score} tier={item.tier} className="shrink-0" />
      <ChevronRight
        className="size-4 shrink-0 text-muted-foreground"
        aria-hidden="true"
      />
    </button>
  );
}
