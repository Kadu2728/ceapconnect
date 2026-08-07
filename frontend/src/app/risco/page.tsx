"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { InterventionDrawer } from "@/features/risk/components/intervention-drawer";
import { RiskQueue } from "@/features/risk/components/risk-queue";

/**
 * Console de Intervenção (EPIC 14 — Predição de evasão). Protegido em duas
 * camadas: sessão (`useRequireAuth`) e papel (coordenador ou admin) — quem
 * não tem acesso é redirecionado ao Dashboard (o backend também barra com
 * 403 por escopo de coorte, defesa em profundidade).
 *
 * O candidato nunca vê esta tela nem o próprio score — regra de negócio, não
 * só UX (o backend recusa a rota para qualquer papel que não seja staff).
 */
export default function RiscoPage() {
  const router = useRouter();
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const isAdmin = storedUser?.is_admin ?? false;
  const isStaff = isAdmin || storedUser?.role === "coordinator";

  const dashboardQuery = useDashboard();
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthorized && storedUser && !isStaff) {
      router.replace("/dashboard");
    }
  }, [isAuthorized, storedUser, isStaff, router]);

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "coordenador";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Console de intervenção"
        title="Risco de evasão"
        description="Candidatos priorizados por risco de abandono, com o motivo em linguagem clara e ação de contato em um clique."
      />

      {isAuthorized && isStaff ? (
        <>
          <RiskQueue onSelectCandidate={setSelectedCandidateId} />
          <InterventionDrawer
            candidateProfileId={selectedCandidateId}
            onClose={() => setSelectedCandidateId(null)}
          />
        </>
      ) : null}
    </AuthenticatedShell>
  );
}
