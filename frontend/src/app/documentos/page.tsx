"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { DocumentsContent } from "@/features/documents/components/documents-content";
import { useDocuments } from "@/features/documents/hooks/use-documents";

/**
 * Tela de Documentos (EPIC 15). Checklist real de upload — ataca diretamente
 * o gargalo que a predição de evasão (EPIC 14) identificou na etapa de
 * Documentação, dando ao candidato um jeito de resolver, não só de ver.
 */
export default function DocumentosPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();
  const documentsQuery = useDocuments();

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
        title="Documentos"
        description="Envie os documentos exigidos para avançar na sua inscrição. Aceitamos foto (JPG/PNG) ou PDF, até 2MB."
      />

      {!isAuthorized || documentsQuery.isPending ? (
        <CardListSkeleton count={3} withSummary />
      ) : documentsQuery.isSuccess ? (
        <DocumentsContent data={documentsQuery.data} />
      ) : (
        <QueryErrorState onRetry={() => documentsQuery.refetch()} />
      )}
    </AuthenticatedShell>
  );
}
