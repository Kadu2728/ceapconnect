"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { AchievementsContent } from "@/features/achievements/components/achievements-content";
import { useAchievements } from "@/features/achievements/hooks/use-achievements";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";

/**
 * Tela de Conquistas (EPIC 06). Mostra o catálogo completo com o status de
 * desbloqueio do candidato — desbloqueadas em destaque, bloqueadas como metas.
 */
export default function ConquistasPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const achievementsQuery = useAchievements();

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        title="Conquistas"
        description="Cada conquista marca uma etapa vencida. Desbloqueie todas ao longo da sua jornada."
      />

      {!isAuthorized || achievementsQuery.isPending ? (
        <CardListSkeleton count={6} withSummary />
      ) : achievementsQuery.isSuccess ? (
        <AchievementsContent data={achievementsQuery.data} />
      ) : (
        <QueryErrorState onRetry={() => achievementsQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
