"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Check } from "lucide-react";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import type {
  DashboardJourney,
  JourneyStepStatus,
} from "@/features/dashboard/types/dashboard.types";
import { cn } from "@/lib/utils";

const STATUS_LABEL: Record<JourneyStepStatus, string> = {
  completed: "concluído",
  current: "em andamento",
  pending: "pendente",
};

function StepIndicator({ status }: { status: JourneyStepStatus }) {
  if (status === "completed") {
    return (
      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-success text-success-foreground">
        <Check className="size-3.5" aria-hidden="true" />
      </span>
    );
  }

  if (status === "current") {
    return (
      <span className="flex size-6 shrink-0 items-center justify-center rounded-full border-2 border-primary">
        <span className="size-2 rounded-full bg-primary" />
      </span>
    );
  }

  return (
    <span
      className="size-6 shrink-0 rounded-full border-2 border-muted"
      aria-hidden="true"
    />
  );
}

interface JourneyProgressProps {
  journey: DashboardJourney;
}

/**
 * Barra de progresso real da jornada do candidato (EPIC 03), com a mesma
 * linguagem visual do preview estático da Landing Page
 * (`features/landing/components/journey-preview.tsx`), agora alimentada
 * pelos dados reais de `GET /api/v1/dashboard`.
 *
 * Cor não é o único indicador de status (WCAG 1.4.1): cada etapa também
 * expõe o status em texto para leitores de tela via `sr-only`.
 */
export function JourneyProgress({ journey }: JourneyProgressProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const percentage = Math.min(100, Math.max(0, Math.round(journey.percentage)));

  return (
    <DashboardCard>
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Sua jornada</h2>
        <span className="text-sm font-semibold text-primary">{percentage}%</span>
      </div>

      <div
        role="progressbar"
        aria-valuenow={percentage}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Progresso da jornada"
        className="mt-5 h-1.5 w-full overflow-hidden rounded-full bg-muted"
      >
        <motion.div
          className="h-full rounded-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: shouldReduceMotion ? 0 : 0.6, ease: "easeOut" }}
        />
      </div>

      <ol className="mt-6 flex flex-col gap-4">
        {journey.steps.map((step) => (
          <li key={step.key} className="flex flex-col gap-1">
            <div className="flex items-center gap-3">
              <StepIndicator status={step.status} />
              <span
                className={cn(
                  "text-sm",
                  step.status === "pending" ? "text-muted-foreground" : "font-medium",
                )}
              >
                {step.label}
                <span className="sr-only"> ({STATUS_LABEL[step.status]})</span>
              </span>
            </div>
            {/* Só a etapa atual mostra o "por quê" — é a que responde à
                pergunta que importa agora; expor a descrição de todas de
                uma vez viraria ruído (§8: clareza, não excesso). */}
            {step.status === "current" ? (
              <p className="ml-9 text-xs text-muted-foreground">{step.description}</p>
            ) : null}
          </li>
        ))}
      </ol>
    </DashboardCard>
  );
}
