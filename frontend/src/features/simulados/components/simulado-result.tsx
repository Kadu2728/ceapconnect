"use client";

import { ArrowLeft, Award, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { FinishAttemptResult } from "@/features/simulados/types/simulado.types";

const SUBJECT_LABEL: Record<string, string> = {
  portugues: "Português",
  matematica: "Matemática",
};

interface SimuladoResultProps {
  result: FinishAttemptResult;
  onRestart: () => void;
}

/**
 * Tela final do simulado: placar, XP ganho e desempenho por matéria — sem
 * nenhuma comparação com outros candidatos, só o progresso pessoal.
 */
export function SimuladoResult({ result, onRestart }: SimuladoResultProps) {
  return (
    <div className="flex flex-col gap-6">
      <Card className="items-center gap-3 py-8 text-center">
        <span className="flex size-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand to-brand-green text-primary-foreground shadow-lg shadow-brand/25">
          <Award className="size-8" aria-hidden="true" />
        </span>
        <p className="text-4xl font-bold tracking-tight">{result.score_percentage}%</p>
        <p className="text-sm text-muted-foreground">
          {result.correct_count} de {result.total_questions} questões corretas
        </p>
        <span className="mt-1 inline-flex items-center gap-1.5 rounded-full bg-accent px-3.5 py-1.5 text-sm font-semibold text-accent-foreground">
          <Sparkles className="size-4" aria-hidden="true" />+{result.xp_awarded} XP
        </span>
      </Card>

      <Card className="gap-3">
        <h3 className="px-6 font-semibold">Desempenho por matéria</h3>
        <div className="flex flex-col gap-3 px-6 pb-2">
          {result.subject_breakdown.map((item) => {
            const percentage =
              item.total > 0 ? Math.round((item.correct / item.total) * 100) : 0;
            return (
              <div key={item.subject}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span>{SUBJECT_LABEL[item.subject] ?? item.subject}</span>
                  <span className="font-medium">
                    {item.correct}/{item.total}
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-brand to-brand-green transition-[width] duration-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <Button variant="outline" onClick={onRestart}>
        <ArrowLeft className="size-4" aria-hidden="true" />
        Voltar ao histórico
      </Button>
    </div>
  );
}
