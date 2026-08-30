"use client";

import { ArrowRight, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { formatFullDate } from "@/features/dashboard/utils/date";
import { useResumePause } from "@/features/journey-os/hooks/use-journey-pause";
import type { PauseState } from "@/features/journey-os/types/journey-os.types";

interface PausedJourneyCardProps {
  pause: PauseState;
  greetingName: string;
}

/**
 * A experiência durante a pausa declarada ("Jornada que Respira").
 *
 * Substitui o Dashboard inteiro, mesmo racional do Modo Resgate: durante a
 * pausa, XP, missões, conquistas e ranking só somariam pressão a quem acabou
 * de dizer que a vida apertou. Sobram três coisas — que guardamos o lugar,
 * até quando, e um caminho de volta de um toque.
 *
 * A volta é a única ação da tela **de propósito**: o design tem que tornar
 * voltar mais leve que ficar fora. Nada aqui cobra, culpa ou fala em atraso.
 */
export function PausedJourneyCard({ pause, greetingName }: PausedJourneyCardProps) {
  const resumePause = useResumePause();

  return (
    <DashboardCard className="flex flex-col gap-5 border-brand/20 bg-brand/[0.03]">
      <div>
        <h1 className="text-xl font-semibold">Guardamos seu lugar, {greetingName}.</h1>
        <p className="mt-2 text-pretty text-muted-foreground">
          Sua jornada está exatamente onde você parou. Não vamos te cobrar nada até{" "}
          <span className="font-medium text-foreground">
            {formatFullDate(pause.ends_at)}
          </span>{" "}
          — e você pode voltar antes disso quando quiser.
        </p>
      </div>

      <Button
        size="lg"
        className="w-full gap-2 sm:w-fit"
        disabled={resumePause.isPending}
        onClick={() => resumePause.mutate()}
      >
        {resumePause.isPending ? (
          <>
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
            Retomando…
          </>
        ) : (
          <>
            Voltar para minha jornada
            <ArrowRight className="size-4" aria-hidden="true" />
          </>
        )}
      </Button>
    </DashboardCard>
  );
}
