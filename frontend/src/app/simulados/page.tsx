"use client";

import { useState } from "react";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { SimuladoHistory } from "@/features/simulados/components/simulado-history";
import { SimuladoResult } from "@/features/simulados/components/simulado-result";
import { SimuladoRunner } from "@/features/simulados/components/simulado-runner";
import { useStartSimulado } from "@/features/simulados/hooks/use-simulado-actions";
import { useSimuladoHistory } from "@/features/simulados/hooks/use-simulado-history";
import type {
  FinishAttemptResult,
  StartAttemptResult,
} from "@/features/simulados/types/simulado.types";

type ViewState =
  | { mode: "idle" }
  | { mode: "running"; attempt: StartAttemptResult }
  | { mode: "result"; result: FinishAttemptResult };

/**
 * Tela de Simulados (EPIC 16). Preparação real para o formato da prova
 * (Português + Matemática, 20 questões), com feedback pessoal e imediato —
 * bem diferente do risk score, que o candidato nunca vê: aqui o desempenho é
 * dele, para ele, sem estigma nenhum.
 */
export default function SimuladosPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const historyQuery = useSimuladoHistory();
  const startMutation = useStartSimulado();
  const [view, setView] = useState<ViewState>({ mode: "idle" });

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  function handleStart() {
    startMutation.mutate(undefined, {
      onSuccess: (attempt) => setView({ mode: "running", attempt }),
    });
  }

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Preparação"
        title="Simulados"
        description="Pratique no formato real da prova — 20 questões objetivas de Português e Matemática, com feedback na hora."
      />

      {view.mode === "running" ? (
        <SimuladoRunner
          attemptId={view.attempt.attempt_id}
          questions={view.attempt.questions}
          onFinished={(result) => setView({ mode: "result", result })}
        />
      ) : view.mode === "result" ? (
        <SimuladoResult
          result={view.result}
          onRestart={() => setView({ mode: "idle" })}
        />
      ) : !isAuthorized || historyQuery.isPending ? (
        <CardListSkeleton count={3} withSummary />
      ) : historyQuery.isSuccess ? (
        <SimuladoHistory
          data={historyQuery.data}
          onStart={handleStart}
          isStarting={startMutation.isPending}
        />
      ) : (
        <QueryErrorState onRetry={() => historyQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
