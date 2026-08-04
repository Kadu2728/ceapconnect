"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { ProfileContent } from "@/features/profile/components/profile-content";
import { useProfile } from "@/features/profile/hooks/use-profile";

/**
 * Tela de Perfil (EPIC 09). Consolida dados cadastrais + gamificação (nível, XP,
 * conquistas, recompensas) e permite editar os dados de contato. Acessível pelo
 * avatar da navbar.
 */
export default function PerfilPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const profileQuery = useProfile();

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Sua conta"
        title="Meu perfil"
        description="Veja o resumo da sua jornada e mantenha seus dados de contato atualizados."
      />

      {!isAuthorized || profileQuery.isPending ? (
        <CardListSkeleton count={3} withSummary />
      ) : profileQuery.isSuccess ? (
        <ProfileContent data={profileQuery.data} />
      ) : (
        <QueryErrorState onRetry={() => profileQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
