"use client";

import { motion, useReducedMotion } from "framer-motion";
import { CheckCircle2, ChevronRight, HeartHandshake } from "lucide-react";
import { useState } from "react";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { Card } from "@/components/ui/card";
import { GuardianDrawer } from "@/features/guardians/components/guardian-drawer";
import { useGuardiansAtRisk } from "@/features/guardians/hooks/use-guardians-at-risk";
import { useSetCohortTrainingDate } from "@/features/guardians/hooks/use-set-cohort-training-date";
import type { GuardianAtRiskItem } from "@/features/guardians/types/guardian.types";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface CohortGroup {
  cohortId: string | null;
  cohortName: string | null;
  trainingDate: string | null;
  items: GuardianAtRiskItem[];
}

/**
 * Alvo duplo do Console de Intervenção + Área de Pais: famílias que
 * precisam de atenção com a formação obrigatória de responsáveis, agrupadas
 * por coorte (a data da formação é definida por coorte, nunca por família).
 */
export function GuardiansAtRisk() {
  const query = useGuardiansAtRisk();
  const [selected, setSelected] = useState<GuardianAtRiskItem | null>(null);

  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  if (query.isPending) {
    return <CardListSkeleton count={3} withSummary />;
  }
  if (!query.isSuccess) {
    return <QueryErrorState onRetry={() => query.refetch()} />;
  }

  const { items, total } = query.data;

  if (items.length === 0) {
    return (
      <Card className="items-center gap-3 py-16 text-center">
        <span className="flex size-14 items-center justify-center rounded-2xl bg-success/10 text-success">
          <CheckCircle2 className="size-7" aria-hidden="true" />
        </span>
        <div className="px-6">
          <h3 className="font-semibold">Nenhuma família pendente</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Todos os responsáveis em risco já foram atendidos — bom sinal.
          </p>
        </div>
      </Card>
    );
  }

  const groups = groupByCohort(items);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2 px-1">
        <HeartHandshake className="size-5 text-brand" aria-hidden="true" />
        <div>
          <p className="text-sm text-muted-foreground">Responsáveis em risco</p>
          <p className="text-2xl font-bold tracking-tight tabular-nums">{total}</p>
        </div>
      </div>

      {groups.map((group) => (
        <CohortGroupCard
          key={group.cohortId ?? "sem-coorte"}
          group={group}
          onSelect={setSelected}
          containerVariants={containerVariants}
          itemVariants={itemVariants}
        />
      ))}

      <GuardianDrawer item={selected} onClose={() => setSelected(null)} />
    </div>
  );
}

function CohortGroupCard({
  group,
  onSelect,
  containerVariants,
  itemVariants,
}: {
  group: CohortGroup;
  onSelect: (item: GuardianAtRiskItem) => void;
  containerVariants: ReturnType<typeof getStaggerContainerVariants>;
  itemVariants: ReturnType<typeof getStaggerItemVariants>;
}) {
  return (
    <Card className="gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3 px-6">
        <h3 className="font-semibold">{group.cohortName ?? "Sem coorte"}</h3>
        {group.cohortId ? (
          <TrainingDateControl
            cohortId={group.cohortId}
            trainingDate={group.trainingDate}
          />
        ) : null}
      </div>

      <motion.ul
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="flex flex-col gap-3 px-6"
      >
        {group.items.map((item) => (
          <motion.li key={item.candidate_profile_id} variants={itemVariants}>
            <GuardianRow item={item} onClick={() => onSelect(item)} />
          </motion.li>
        ))}
      </motion.ul>
    </Card>
  );
}

function TrainingDateControl({
  cohortId,
  trainingDate,
}: {
  cohortId: string;
  trainingDate: string | null;
}) {
  const [value, setValue] = useState(trainingDate ?? "");
  const mutation = useSetCohortTrainingDate();

  return (
    <form
      className="flex items-center gap-2"
      onSubmit={(event) => {
        event.preventDefault();
        mutation.mutate({ cohortId, guardianTrainingDate: value || null });
      }}
    >
      <label
        htmlFor={`training-date-${cohortId}`}
        className="text-xs text-muted-foreground"
      >
        Data da formação
      </label>
      <input
        id={`training-date-${cohortId}`}
        type="date"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        className="rounded-md border border-input bg-transparent px-2 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
      />
      <button
        type="submit"
        disabled={mutation.isPending}
        className="rounded-md border border-input px-2 py-1 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent/50"
      >
        Salvar
      </button>
    </form>
  );
}

function GuardianRow({
  item,
  onClick,
}: {
  item: GuardianAtRiskItem;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center gap-4 rounded-xl border bg-card px-5 py-4 text-left transition-all hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-md"
    >
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="font-medium">{item.candidate_name}</p>
          {item.guardian_name ? (
            <span className="text-xs text-muted-foreground">
              responsável: {item.guardian_name}
            </span>
          ) : null}
        </div>
        <p className="mt-1.5 text-sm text-muted-foreground">{item.reason}</p>
      </div>
      <ChevronRight
        className="size-4 shrink-0 text-muted-foreground"
        aria-hidden="true"
      />
    </button>
  );
}

function groupByCohort(items: GuardianAtRiskItem[]): CohortGroup[] {
  const map = new Map<string, CohortGroup>();
  for (const item of items) {
    const key = item.cohort_id ?? "sem-coorte";
    const existing = map.get(key);
    if (existing) {
      existing.items.push(item);
      continue;
    }
    map.set(key, {
      cohortId: item.cohort_id,
      cohortName: item.cohort_name,
      trainingDate: item.guardian_training_date,
      items: [item],
    });
  }
  return Array.from(map.values());
}
