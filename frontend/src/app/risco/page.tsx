"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { GuardiansAtRisk } from "@/features/guardians/components/guardians-at-risk";
import { InterventionDrawer } from "@/features/risk/components/intervention-drawer";
import { RiskQueue } from "@/features/risk/components/risk-queue";
import { cn } from "@/lib/utils";

type ConsoleTab = "candidatos" | "responsaveis";

const TABS: { value: ConsoleTab; label: string }[] = [
  { value: "candidatos", label: "Candidatos" },
  { value: "responsaveis", label: "Responsáveis · Área de Pais" },
];

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
  const [activeTab, setActiveTab] = useState<ConsoleTab>("candidatos");

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
        description="Candidatos e responsáveis priorizados por risco, com o motivo em linguagem clara e ação de contato em um clique."
      />

      {isAuthorized && isStaff ? (
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap gap-2">
            {TABS.map((tab) => (
              <button
                key={tab.value}
                type="button"
                aria-pressed={activeTab === tab.value}
                onClick={() => setActiveTab(tab.value)}
                className={cn(
                  "rounded-md border px-3 py-1.5 text-sm font-medium transition-colors",
                  activeTab === tab.value
                    ? "border-brand bg-brand/10 text-brand"
                    : "border-input text-muted-foreground hover:bg-accent/50",
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === "candidatos" ? (
            <>
              <RiskQueue onSelectCandidate={setSelectedCandidateId} />
              <InterventionDrawer
                candidateProfileId={selectedCandidateId}
                onClose={() => setSelectedCandidateId(null)}
              />
            </>
          ) : (
            <GuardiansAtRisk />
          )}
        </div>
      ) : null}
    </AuthenticatedShell>
  );
}
