"use client";

import { Check, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  useAnswerQuestion,
  useFinishSimulado,
} from "@/features/simulados/hooks/use-simulado-actions";
import type {
  AnswerResult,
  FinishAttemptResult,
  SimuladoQuestion,
} from "@/features/simulados/types/simulado.types";
import { cn } from "@/lib/utils";

const SUBJECT_LABEL: Record<string, string> = {
  portugues: "Português",
  matematica: "Matemática",
};

interface SimuladoRunnerProps {
  attemptId: string;
  questions: SimuladoQuestion[];
  onFinished: (result: FinishAttemptResult) => void;
}

/**
 * Fluxo de resposta do simulado, uma questão por vez: selecionar uma opção já
 * envia a resposta e mostra o feedback imediatamente (certo/errado + a
 * explicação) — é o valor pedagógico da ferramenta. "Próxima questão" só
 * aparece depois da resposta, evitando pular sem ver o feedback.
 */
export function SimuladoRunner({
  attemptId,
  questions,
  onFinished,
}: SimuladoRunnerProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOptionKey, setSelectedOptionKey] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<AnswerResult | null>(null);
  const answerMutation = useAnswerQuestion();
  const finishMutation = useFinishSimulado();

  const question = questions[currentIndex];
  // `currentIndex` é sempre um índice válido de `questions` (nasce em 0 e só
  // avança até `questions.length - 1`) — a guarda existe só para satisfazer o
  // `noUncheckedIndexedAccess` do TypeScript, nunca deve renderizar `null` de
  // fato. Precisa vir antes de `handleSelect`/`handleContinue`: o narrowing de
  // `question` só se propaga para dentro das closures se a guarda já tiver
  // acontecido no momento em que elas são declaradas.
  if (!question) return null;

  const isLast = currentIndex === questions.length - 1;
  const isAnswered = feedback !== null;
  const progress = Math.round(
    ((currentIndex + (isAnswered ? 1 : 0)) / questions.length) * 100,
  );

  function handleSelect(optionKey: string) {
    // Deriva de novo dentro da closure: o narrowing de `question` no corpo do
    // componente não se propaga para dentro de `function` declarations no
    // TypeScript — refazer o acesso aqui narrowa localmente.
    const currentQuestion = questions[currentIndex];
    if (isAnswered || answerMutation.isPending || !currentQuestion) return;
    setSelectedOptionKey(optionKey);
    answerMutation.mutate(
      { attemptId, questionId: currentQuestion.id, selectedOptionKey: optionKey },
      { onSuccess: setFeedback },
    );
  }

  function handleContinue() {
    if (isLast) {
      finishMutation.mutate(attemptId, { onSuccess: onFinished });
      return;
    }
    setCurrentIndex((index) => index + 1);
    setSelectedOptionKey(null);
    setFeedback(null);
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">
          Questão {currentIndex + 1} de {questions.length}
        </span>
        <span className="rounded-full bg-accent px-2.5 py-1 text-xs font-semibold text-accent-foreground">
          {SUBJECT_LABEL[question.subject] ?? question.subject}
        </span>
      </div>

      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-gradient-to-r from-brand to-brand-green transition-[width] duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <Card className="gap-4">
        <p className="px-6 font-medium">{question.statement}</p>

        <div className="flex flex-col gap-2 px-6">
          {question.options.map((option) => {
            const isThisSelected = option.key === selectedOptionKey;
            const isThisCorrect =
              isAnswered && option.key === feedback.correct_option_key;
            const isThisWrong = isAnswered && isThisSelected && !feedback.is_correct;

            return (
              <button
                key={option.key}
                type="button"
                onClick={() => handleSelect(option.key)}
                disabled={isAnswered || answerMutation.isPending}
                className={cn(
                  "flex items-center gap-3 rounded-lg border px-4 py-3 text-left text-sm transition-colors disabled:cursor-default",
                  !isAnswered && "hover:border-brand/40 hover:bg-accent/40",
                  isThisCorrect && "border-success bg-success/10",
                  isThisWrong && "border-destructive bg-destructive/10",
                )}
              >
                <span
                  className={cn(
                    "flex size-6 shrink-0 items-center justify-center rounded-full border text-xs font-semibold uppercase text-muted-foreground",
                    isThisCorrect && "border-success bg-success text-white",
                    isThisWrong && "border-destructive bg-destructive text-white",
                  )}
                >
                  {isThisCorrect ? (
                    <Check className="size-3.5" aria-hidden="true" />
                  ) : isThisWrong ? (
                    <X className="size-3.5" aria-hidden="true" />
                  ) : (
                    option.key
                  )}
                </span>
                {option.text}
              </button>
            );
          })}
        </div>

        {feedback ? (
          <div
            className={cn(
              "mx-6 rounded-lg px-4 py-3 text-sm",
              feedback.is_correct
                ? "bg-success/10 text-success"
                : "bg-destructive/10 text-destructive",
            )}
          >
            <p className="font-semibold">
              {feedback.is_correct ? "Você acertou!" : "Não foi dessa vez"}
            </p>
            <p className="mt-1 text-foreground/80">{feedback.explanation}</p>
          </div>
        ) : null}

        {feedback ? (
          <div className="px-6">
            <Button onClick={handleContinue} disabled={finishMutation.isPending}>
              {isLast
                ? finishMutation.isPending
                  ? "Calculando…"
                  : "Ver resultado"
                : "Próxima questão"}
            </Button>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
