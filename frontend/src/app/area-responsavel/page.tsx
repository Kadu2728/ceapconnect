"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { GuardianShell } from "@/components/layout/guardian-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { GuardianChildrenList } from "@/features/guardian-access/components/guardian-children-list";
import { LinkGuardianChildForm } from "@/features/guardian-access/components/link-guardian-child-form";
import { useGuardianChildren } from "@/features/guardian-access/hooks/use-guardian-children";

/**
 * Área do Responsável (RBAC do responsável — fase B): lista dos filhos
 * vinculados e autorizados à conta. Protegida em duas camadas, mesmo padrão
 * de `/admin`: sessão (`useRequireAuth`) + papel (`role === "guardian"`,
 * candidatos comuns são redirecionados ao Dashboard) — o backend também
 * barra com 403 (defesa em profundidade).
 */
export default function AreaResponsavelPage() {
  const router = useRouter();
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const isGuardian = storedUser?.role === "guardian";

  const childrenQuery = useGuardianChildren();

  useEffect(() => {
    if (isAuthorized && storedUser && !isGuardian) {
      router.replace("/dashboard");
    }
  }, [isAuthorized, storedUser, isGuardian, router]);

  return (
    <GuardianShell userName={storedUser?.name ?? "responsável"}>
      <PageHeader
        eyebrow="Área do responsável"
        title="Seus candidatos"
        description="Acompanhe o progresso na jornada — nunca a nota ou o desempenho."
      />

      {!isAuthorized || !isGuardian || childrenQuery.isPending ? (
        <CardListSkeleton count={2} />
      ) : childrenQuery.isSuccess ? (
        <div className="flex flex-col gap-6">
          {childrenQuery.data.pending_consent_count > 0 ? (
            <div className="rounded-xl border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning">
              {childrenQuery.data.pending_consent_count === 1
                ? "1 vínculo aguardando autorização do candidato — peça para ele confirmar no perfil dele."
                : `${childrenQuery.data.pending_consent_count} vínculos aguardando autorização do candidato — peça para eles confirmarem no perfil.`}
            </div>
          ) : null}
          <GuardianChildrenList items={childrenQuery.data.children} />
          <LinkGuardianChildForm />
        </div>
      ) : (
        <QueryErrorState onRetry={() => childrenQuery.refetch()} />
      )}
    </GuardianShell>
  );
}
