"use client";

import { useState } from "react";

import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { DashboardContent } from "@/features/dashboard/components/dashboard-content";
import { DashboardErrorState } from "@/features/dashboard/components/dashboard-error-state";
import { DashboardSkeleton } from "@/features/dashboard/components/dashboard-skeleton";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { WelcomeOnboarding } from "@/features/onboarding/components/welcome-onboarding";
import { useCompleteOnboarding } from "@/features/onboarding/hooks/use-complete-onboarding";

/**
 * Dashboard (EPIC 03) — o centro da experiência do candidato.
 *
 * Responde de imediato às quatro perguntas de USER_FLOW.md ("Onde estou?",
 * "O que preciso fazer?", "Quanto falta?", "Qual minha próxima etapa?"). No
 * primeiro login, exibe a tela de boas-vindas (`onboarded: false`).
 */
export default function DashboardPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const completeOnboarding = useCompleteOnboarding();
  const [welcomeDismissed, setWelcomeDismissed] = useState(false);

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  const showWelcome =
    dashboardQuery.isSuccess && !dashboardQuery.data.onboarded && !welcomeDismissed;

  const handleFinishWelcome = () => {
    setWelcomeDismissed(true); // fecha na hora; o backend registra em seguida
    completeOnboarding.mutate();
  };

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      {!isAuthorized || dashboardQuery.isPending ? (
        <DashboardSkeleton />
      ) : dashboardQuery.isSuccess ? (
        <DashboardContent data={dashboardQuery.data} />
      ) : (
        <div className="flex min-h-[60vh] items-center justify-center">
          <DashboardErrorState onRetry={() => dashboardQuery.refetch()} />
        </div>
      )}

      {showWelcome ? (
        <WelcomeOnboarding
          name={displayName}
          onFinish={handleFinishWelcome}
          isFinishing={completeOnboarding.isPending}
        />
      ) : null}
    </AuthenticatedShell>
  );
}
