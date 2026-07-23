"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { MissionsContent } from "@/features/missions/components/missions-content";
import { useMissions } from "@/features/missions/hooks/use-missions";

/**
 * Tela de Missões (EPIC 05). Lista todas as missões do candidato e permite
 * concluí-las, com XP e conquistas reais. Nome e contador de notificações da
 * navbar vêm do cache compartilhado do Dashboard (react-query dedupe).
 */
export default function MissoesPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const missionsQuery = useMissions();

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Sua jornada"
        title="Missões"
        description="Complete missões para ganhar XP, desbloquear conquistas e avançar na sua jornada."
      />

      {!isAuthorized || missionsQuery.isPending ? (
        <CardListSkeleton withSummary />
      ) : missionsQuery.isSuccess ? (
        <MissionsContent data={missionsQuery.data} />
      ) : (
        <QueryErrorState onRetry={() => missionsQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
