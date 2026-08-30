"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useStartPause } from "@/features/journey-os/hooks/use-journey-pause";
import type { PauseReasonCode } from "@/features/journey-os/types/journey-os.types";
import { cn } from "@/lib/utils";

/** Mesmas opções que o backend aceita (`journey_pause_rules.PAUSE_OPTION_DAYS`). */
const PERIOD_OPTIONS: { days: number; label: string }[] = [
  { days: 3, label: "Uns dias" },
  { days: 7, label: "Uma semana" },
];

const REASON_OPTIONS: { code: PauseReasonCode; label: string }[] = [
  { code: "trabalho", label: "Trabalho" },
  { code: "tempo", label: "Falta de tempo" },
  { code: "outro", label: "Outro" },
];

/**
 * Controle da Pausa Declarada ("Jornada que Respira").
 *
 * Deliberadamente **discreto**: um link de texto, peso visual baixo, no fim
 * da jornada — nunca um botão que compita com o próximo passo. A pausa
 * precisa existir como saída honesta, mas não pode ser mais convidativa que
 * continuar.
 *
 * Expansão inline em vez de modal: para duas opções, um modal seria mais
 * cerimônia que a decisão merece — e sobrepor a tela num momento em que a
 * pessoa já está sobrecarregada é o oposto de aliviar.
 */
export function PauseControl() {
  const [isOpen, setIsOpen] = useState(false);
  const [reason, setReason] = useState<PauseReasonCode | null>(null);
  const startPause = useStartPause();

  if (!isOpen) {
    return (
      <div className="flex justify-center">
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="rounded-md px-3 py-2 text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-foreground hover:underline"
        >
          Preciso de uns dias
        </button>
      </div>
    );
  }

  return (
    <section
      aria-label="Pausar minha jornada"
      className="rounded-2xl border bg-card p-6 shadow-sm"
    >
      <h2 className="text-base font-semibold">Sem problema — a vida acontece.</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        A gente guarda seu lugar e para de te cobrar por uns dias. Avisos de data marcada,
        como a prova, continuam chegando.
      </p>

      <fieldset className="mt-5">
        <legend className="text-sm font-medium">Por quanto tempo?</legend>
        <div className="mt-2 flex flex-wrap gap-2">
          {PERIOD_OPTIONS.map((option) => (
            <Button
              key={option.days}
              variant="outline"
              disabled={startPause.isPending}
              onClick={() =>
                startPause.mutate({ days: option.days, reason_code: reason })
              }
            >
              {startPause.isPending ? (
                <Loader2 className="size-4 animate-spin" aria-hidden="true" />
              ) : null}
              {option.label}
            </Button>
          ))}
        </div>
      </fieldset>

      <fieldset className="mt-5">
        <legend className="text-sm font-medium">
          Quer contar o motivo?{" "}
          <span className="font-normal text-muted-foreground">(opcional)</span>
        </legend>
        <div className="mt-2 flex flex-wrap gap-2">
          {REASON_OPTIONS.map((option) => {
            const isSelected = reason === option.code;
            return (
              <button
                key={option.code}
                type="button"
                aria-pressed={isSelected}
                onClick={() => setReason(isSelected ? null : option.code)}
                className={cn(
                  "rounded-full border px-3 py-1.5 text-sm transition-colors",
                  isSelected
                    ? "border-brand bg-brand/10 text-brand"
                    : "border-input text-muted-foreground hover:bg-accent/50",
                )}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </fieldset>

      <button
        type="button"
        onClick={() => setIsOpen(false)}
        disabled={startPause.isPending}
        className="mt-5 text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
      >
        Deixa pra lá, quero continuar
      </button>
    </section>
  );
}
