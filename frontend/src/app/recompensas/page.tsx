"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { RewardsContent } from "@/features/rewards/components/rewards-content";
import { useRewards } from "@/features/rewards/hooks/use-rewards";

/**
 * Tela de Recompensas (EPIC 13). Mostra o nível do candidato e o catálogo de
 * cursos/certificações reais — desbloqueados por nível ou conquista e resgatáveis
 * quando disponíveis. É a ponta tangível da gamificação: esforço → prêmio real.
 */
export default function RecompensasPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const rewardsQuery = useRewards();

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Seus prêmios"
        title="Recompensas"
        description="Suba de nível e conclua conquistas para desbloquear cursos e certificações reais. Cada esforço vira um prêmio na sua mão."
      />

      {!isAuthorized || rewardsQuery.isPending ? (
        <CardListSkeleton count={6} withSummary />
      ) : rewardsQuery.isSuccess ? (
        <RewardsContent data={rewardsQuery.data} />
      ) : (
        <QueryErrorState onRetry={() => rewardsQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
