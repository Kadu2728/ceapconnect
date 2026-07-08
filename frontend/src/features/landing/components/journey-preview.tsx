"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Check, Sparkles } from "lucide-react";

import { cn } from "@/lib/utils";

type StepStatus = "done" | "current" | "upcoming";

interface JourneyStep {
  label: string;
  status: StepStatus;
}

/**
 * Etapas ilustrativas exibidas na prévia do Hero (ver "Jornada" em
 * USER_FLOW.md). Valores fixos, apenas para apresentação — a jornada real,
 * por candidato, vive no Dashboard.
 */
const JOURNEY_STEPS: JourneyStep[] = [
  { label: "Inscrição concluída", status: "done" },
  { label: "Documentação enviada", status: "done" },
  { label: "Preparação para a prova", status: "current" },
  { label: "Prova e entrevista", status: "upcoming" },
  { label: "Resultado", status: "upcoming" },
];

const PROGRESS_PERCENT = 62;

const STATUS_LABEL: Record<StepStatus, string> = {
  done: "concluído",
  current: "em andamento",
  upcoming: "pendente",
};

function StepIndicator({ status }: { status: StepStatus }) {
  if (status === "done") {
    return (
      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-success text-success-foreground">
        <Check className="size-3.5" aria-hidden="true" />
      </span>
    );
  }

  if (status === "current") {
    return (
      <span className="relative flex size-6 shrink-0 items-center justify-center rounded-full border-2 border-brand">
        <span className="size-2 rounded-full bg-brand" />
        <span className="absolute inset-0 animate-ping rounded-full border-2 border-brand/40" />
      </span>
    );
  }

  return (
    <span
      className="size-6 shrink-0 rounded-full border-2 border-dashed border-muted-foreground/30"
      aria-hidden="true"
    />
  );
}

/**
 * Prévia visual da jornada do candidato, exibida no Hero.
 *
 * Decisão de UX: em vez de só prometer "acompanhe sua jornada", mostramos como
 * isso se parece — reduz abstração e aumenta confiança (referência: hero com
 * "product preview" da Stripe/Linear). Cor nunca é o único indicador de status
 * (WCAG 1.4.1): cada etapa expõe o status em texto via `sr-only`.
 */
export function JourneyPreviewCard() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className="relative w-full max-w-sm">
      {/* Glow de marca por trás do card */}
      <div
        aria-hidden="true"
        className="absolute -inset-4 -z-10 rounded-[2rem] bg-gradient-to-br from-brand/25 via-brand-green/15 to-transparent blur-2xl"
      />

      <div className="rounded-3xl border border-border/70 bg-card/80 p-6 shadow-xl shadow-brand/5 backdrop-blur-sm">
        <div className="mb-5 flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
              Sua jornada
            </span>
            <span className="text-sm font-semibold text-foreground">
              Processo Seletivo CEAP
            </span>
          </div>
          <span className="inline-flex items-center gap-1 rounded-full bg-success/10 px-2.5 py-1 text-xs font-semibold text-success">
            <Sparkles className="size-3" aria-hidden="true" />
            +240 XP
          </span>
        </div>

        <div className="mb-6">
          <div className="mb-2 flex items-center justify-between text-xs font-medium text-muted-foreground">
            <span>Progresso</span>
            <span className="text-brand">{PROGRESS_PERCENT}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-brand to-brand-green"
              initial={{ width: shouldReduceMotion ? `${PROGRESS_PERCENT}%` : 0 }}
              whileInView={{ width: `${PROGRESS_PERCENT}%` }}
              viewport={{ once: true }}
              transition={{
                duration: shouldReduceMotion ? 0 : 1.1,
                ease: "easeOut",
                delay: 0.2,
              }}
            />
          </div>
        </div>

        <ol className="flex flex-col gap-4">
          {JOURNEY_STEPS.map((step) => (
            <li key={step.label} className="flex items-center gap-3">
              <StepIndicator status={step.status} />
              <span
                className={cn(
                  "text-sm",
                  step.status === "upcoming"
                    ? "text-muted-foreground"
                    : "font-medium text-foreground",
                )}
              >
                {step.label}
                <span className="sr-only"> ({STATUS_LABEL[step.status]})</span>
              </span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
