"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef } from "react";

import { Button } from "@/components/ui/button";
import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { useTrackCandidateEvent } from "@/features/journey-os/hooks/use-track-candidate-event";
import type { NextBestAction } from "@/features/journey-os/types/journey-os.types";
import { NEXT_BEST_ACTION_ROUTES } from "@/features/journey-os/utils/next-best-action-routes";

interface RecoveryModeCardProps {
  action: NextBestAction;
  currentStepLabel: string;
}

/**
 * Modo Resgate (N4) + Zero-Click Recovery (N3): quando `CandidateState.
 * momentum` é "stalled"/"recovery", `dashboard-content.tsx` troca a grade
 * inteira por só este card — uma ação, um CTA, sem gamificação competindo
 * por atenção (brief §5/§8: "sem alarmismo, sem culpa, sem manipulação").
 *
 * "Você estava aqui" + a mesma recomendação do Next Best Action (N2) são a
 * mesma superfície de propósito: mostrar as duas juntas numa tela já
 * reduzida seria a complexidade que este modo existe para evitar.
 */
export function RecoveryModeCard({ action, currentStepLabel }: RecoveryModeCardProps) {
  const { mutate: trackEvent } = useTrackCandidateEvent();
  const hasTrackedEntry = useRef(false);

  useEffect(() => {
    if (hasTrackedEntry.current) return;
    hasTrackedEntry.current = true;
    trackEvent({ name: "recovery_entered" });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- dispara uma única vez, na entrada do modo.
  }, []);

  const href = NEXT_BEST_ACTION_ROUTES[action.action_key];

  return (
    <DashboardCard className="flex flex-col gap-4 border-brand/30 bg-brand/[0.03]">
      <div>
        <p className="text-sm text-muted-foreground">Vimos que você parou aqui:</p>
        <h2 className="text-lg font-semibold">{currentStepLabel}</h2>
      </div>

      {action.why.length > 0 ? (
        <p className="text-sm text-muted-foreground">{action.why.join(" · ")}</p>
      ) : null}

      <Button
        asChild
        size="lg"
        className="w-full gap-2 sm:w-fit"
        onClick={() =>
          trackEvent({ name: "step_resumed", props: { action_key: action.action_key } })
        }
      >
        <Link href={href}>
          Continuar
          <ArrowRight className="size-4" aria-hidden="true" />
        </Link>
      </Button>
    </DashboardCard>
  );
}
