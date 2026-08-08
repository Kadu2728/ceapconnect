"use client";

import { CalendarClock, PlayCircle, Trophy } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { AttemptHistory } from "@/features/simulados/types/simulado.types";
import { cn } from "@/lib/utils";

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

interface SimuladoHistoryProps {
  data: AttemptHistory;
  onStart: () => void;
  isStarting: boolean;
}

/**
 * Tela inicial dos Simulados: melhor resultado + histórico pessoal (nunca
 * comparado com o de outros candidatos) + ação de começar um novo.
 */
export function SimuladoHistory({ data, onStart, isStarting }: SimuladoHistoryProps) {
  return (
    <div className="flex flex-col gap-6">
      <Card className="items-center gap-4 py-8 text-center">
        <span className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand/15 to-brand-green/15 text-brand">
          <Trophy className="size-7" aria-hidden="true" />
        </span>
        <div>
          <p className="text-sm text-muted-foreground">
            {data.best_score_percentage !== null
              ? "Sua melhor pontuação"
              : "Nenhum simulado ainda"}
          </p>
          <p className="text-3xl font-bold tracking-tight">
            {data.best_score_percentage !== null ? `${data.best_score_percentage}%` : "—"}
          </p>
        </div>
        <Button onClick={onStart} disabled={isStarting}>
          <PlayCircle className="size-4" aria-hidden="true" />
          {isStarting
            ? "Preparando…"
            : data.attempts.length > 0
              ? "Fazer novo simulado"
              : "Começar meu primeiro simulado"}
        </Button>
        <p className="max-w-sm text-xs text-muted-foreground">
          20 questões (Português + Matemática), no mesmo formato da prova real. Feedback
          na hora, em cada questão.
        </p>
      </Card>

      {data.attempts.length > 0 ? (
        <Card className="gap-3">
          <h3 className="px-6 font-semibold">Histórico</h3>
          <ul className="divide-y divide-border/60">
            {data.attempts.map((attempt) => (
              <li
                key={attempt.attempt_id}
                className="flex items-center justify-between gap-3 px-6 py-3"
              >
                <span className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CalendarClock className="size-4 shrink-0" aria-hidden="true" />
                  {formatDate(attempt.finished_at)}
                </span>
                <span
                  className={cn(
                    "text-sm font-semibold tabular-nums",
                    attempt.score_percentage >= 70 ? "text-success" : "text-foreground",
                  )}
                >
                  {attempt.correct_count}/{attempt.total_questions} ·{" "}
                  {attempt.score_percentage}%
                </span>
              </li>
            ))}
          </ul>
        </Card>
      ) : null}
    </div>
  );
}
