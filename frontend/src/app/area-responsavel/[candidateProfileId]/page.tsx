"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { GuardianShell } from "@/components/layout/guardian-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { GuardianChildJourneyView } from "@/features/guardian-access/components/guardian-child-journey-view";
import { useGuardianChildJourney } from "@/features/guardian-access/hooks/use-guardian-child-journey";

/**
 * Jornada essencial de um filho, visão do responsável (RBAC do responsável
 * — fase B). Mesmo guard duplo de `/area-responsavel`; um `candidateProfileId`
 * fora do escopo do responsável autenticado nunca resolve dado nenhum — o
 * backend responde 403 antes de ler qualquer campo do candidato.
 */
export default function AreaResponsavelChildPage() {
  const router = useRouter();
  const params = useParams<{ candidateProfileId: string }>();
  const candidateProfileId = params.candidateProfileId;

  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const isGuardian = storedUser?.role === "guardian";

  const journeyQuery = useGuardianChildJourney(candidateProfileId);

  useEffect(() => {
    if (isAuthorized && storedUser && !isGuardian) {
      router.replace("/dashboard");
    }
  }, [isAuthorized, storedUser, isGuardian, router]);

  return (
    <GuardianShell userName={storedUser?.name ?? "responsável"}>
      <Link
        href="/area-responsavel"
        className="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Meus candidatos
      </Link>

      {!isAuthorized || !isGuardian || journeyQuery.isPending ? (
        <>
          <PageHeader eyebrow="Área do responsável" title="Carregando…" />
          <CardListSkeleton count={3} />
        </>
      ) : journeyQuery.isSuccess ? (
        <>
          <PageHeader
            eyebrow="Área do responsável"
            title={journeyQuery.data.candidate_name}
            description="Progresso na jornada — nunca a nota ou o desempenho."
          />
          <GuardianChildJourneyView data={journeyQuery.data} />
        </>
      ) : (
        <QueryErrorState onRetry={() => journeyQuery.refetch()} />
      )}
    </GuardianShell>
  );
}
