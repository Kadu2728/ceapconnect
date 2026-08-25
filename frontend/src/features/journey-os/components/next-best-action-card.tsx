"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { createElement } from "react";

import { Button } from "@/components/ui/button";
import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { useTrackCandidateEvent } from "@/features/journey-os/hooks/use-track-candidate-event";
import type { NextBestAction } from "@/features/journey-os/types/journey-os.types";
import {
  NEXT_BEST_ACTION_ICONS,
  NEXT_BEST_ACTION_ROUTES,
} from "@/features/journey-os/utils/next-best-action-routes";

interface NextBestActionCardProps {
  action: NextBestAction;
}

/**
 * Uma ação, um CTA, um "por quê" (Candidate Journey OS — N2). Substitui o
 * card de "missão do dia" quando há algo mais urgente a resolver — ver
 * `dashboard-content.tsx` para a regra de qual dos dois aparece.
 */
export function NextBestActionCard({ action }: NextBestActionCardProps) {
  const { mutate: trackEvent } = useTrackCandidateEvent();
  const Icon = NEXT_BEST_ACTION_ICONS[action.action_key];
  const href = NEXT_BEST_ACTION_ROUTES[action.action_key];

  return (
    <DashboardCard className="flex flex-col gap-4">
      <span className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
        Sua próxima ação
      </span>

      <div className="flex items-start gap-3">
        <span className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-brand/10 text-brand">
          {createElement(Icon, { className: "size-6", "aria-hidden": true })}
        </span>
        <div className="min-w-0">
          <h2 className="text-lg font-semibold">{action.cta_label}</h2>
          {action.why.length > 0 ? (
            <p className="text-sm text-muted-foreground">{action.why.join(" · ")}</p>
          ) : null}
        </div>
      </div>

      <Button
        asChild
        className="mt-2 w-full gap-2 sm:w-fit"
        onClick={() =>
          trackEvent({ name: "nba_clicked", props: { action_key: action.action_key } })
        }
      >
        <Link href={href}>
          {action.cta_label}
          <ArrowRight className="size-4" aria-hidden="true" />
        </Link>
      </Button>
    </DashboardCard>
  );
}
