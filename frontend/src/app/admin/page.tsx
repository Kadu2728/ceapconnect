"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { AdminContent } from "@/features/admin/components/admin-content";
import { RedemptionsPanel } from "@/features/admin/components/redemptions-panel";
import { RewardsManager } from "@/features/admin/components/rewards-manager";
import { useAdminOverview } from "@/features/admin/hooks/use-admin-overview";
import { useAdminRewards } from "@/features/admin/hooks/use-admin-rewards";
import { useRedemptions } from "@/features/admin/hooks/use-redemptions";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";

/**
 * Painel administrativo (EPIC 10). Protegido em duas camadas: sessão
 * (`useRequireAuth`) e papel de admin — candidatos comuns são redirecionados ao
 * Dashboard (o backend também barra com 403, defesa em profundidade).
 */
export default function AdminPage() {
  const router = useRouter();
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const isAdmin = storedUser?.is_admin ?? false;

  const dashboardQuery = useDashboard();
  const overviewQuery = useAdminOverview();
  const redemptionsQuery = useRedemptions();
  const rewardsQuery = useAdminRewards();

  useEffect(() => {
    if (isAuthorized && storedUser && !isAdmin) {
      router.replace("/dashboard");
    }
  }, [isAuthorized, storedUser, isAdmin, router]);

  const displayName = dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "admin";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Gestão"
        title="Painel administrativo"
        description="Acompanhe o acesso, o engajamento e a gamificação dos alunos em tempo real."
      />

      {!isAuthorized || !isAdmin || overviewQuery.isPending ? (
        <CardListSkeleton count={4} withSummary />
      ) : overviewQuery.isSuccess ? (
        <div className="flex flex-col gap-6">
          <AdminContent data={overviewQuery.data} />
          {rewardsQuery.isSuccess ? <RewardsManager data={rewardsQuery.data} /> : null}
          {redemptionsQuery.isSuccess ? (
            <RedemptionsPanel data={redemptionsQuery.data} />
          ) : null}
        </div>
      ) : (
        <QueryErrorState onRetry={() => overviewQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
