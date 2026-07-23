"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { EventsContent } from "@/features/events/components/events-content";
import { useEvents } from "@/features/events/hooks/use-events";

/**
 * Tela de Eventos (EPIC 07). Lista os próximos eventos e permite inscrever-se
 * ou cancelar — a inscrição gera uma notificação real no sino.
 */
export default function EventosPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const eventsQuery = useEvents();

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Agenda"
        title="Eventos"
        description="Participe de palestras, encontros e simulados. Inscreva-se e receba os lembretes."
      />

      {!isAuthorized || eventsQuery.isPending ? (
        <CardListSkeleton />
      ) : eventsQuery.isSuccess ? (
        <EventsContent data={eventsQuery.data} />
      ) : (
        <QueryErrorState onRetry={() => eventsQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
