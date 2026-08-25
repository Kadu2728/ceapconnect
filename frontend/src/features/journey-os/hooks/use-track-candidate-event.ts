"use client";

import { useMutation } from "@tanstack/react-query";

import { trackCandidateEvent } from "@/features/journey-os/services/journey-os.service";
import type { CandidateTrackableEvent } from "@/features/journey-os/types/journey-os.types";

/**
 * Dispara um evento de telemetria (`nba_clicked`, `step_resumed`,
 * `recovery_*`). Deliberadamente sem `onError`/toast: telemetria nunca deve
 * virar um erro visível para o candidato (mesmo princípio do backend —
 * `activity_event_service`: best-effort, engole falha).
 */
export function useTrackCandidateEvent() {
  return useMutation({
    mutationFn: ({
      name,
      props,
    }: {
      name: CandidateTrackableEvent;
      props?: Record<string, unknown>;
    }) => trackCandidateEvent(name, props),
  });
}
