"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { NotificationsContent } from "@/features/notifications/components/notifications-content";
import { useNotifications } from "@/features/notifications/hooks/use-notifications";
import { PushNotificationsCard } from "@/features/push/components/push-notifications-card";

/**
 * Central de Notificações (EPIC 08). Lista os avisos do candidato (eventos,
 * missões, recompensas, sistema) e permite marcá-los como lidos. É o destino do
 * sino da navbar — fecha o ciclo "fui notificado → onde leio?".
 */
export default function NotificacoesPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const notificationsQuery = useNotifications();

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Seus avisos"
        title="Notificações"
        description="Acompanhe tudo o que acontece na sua jornada — eventos, missões, recompensas e lembretes."
      />

      <div className="mb-4">
        <PushNotificationsCard />
      </div>

      {!isAuthorized || notificationsQuery.isPending ? (
        <CardListSkeleton count={5} />
      ) : notificationsQuery.isSuccess ? (
        <NotificationsContent data={notificationsQuery.data} />
      ) : (
        <QueryErrorState onRetry={() => notificationsQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
