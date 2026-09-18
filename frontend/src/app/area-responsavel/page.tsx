"use client";

import { CardListSkeleton } from "@/components/feedback/card-list-skeleton";
import { QueryErrorState } from "@/components/feedback/query-error-state";
import { GuardianShell } from "@/components/layout/guardian-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireGuardian } from "@/features/auth/hooks/use-require-guardian";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { GuardianChildrenList } from "@/features/guardian-access/components/guardian-children-list";
import { LinkGuardianChildForm } from "@/features/guardian-access/components/link-guardian-child-form";
import { useGuardianChildren } from "@/features/guardian-access/hooks/use-guardian-children";
import { ContinueLessonCard } from "@/features/learning/components/continue-lesson-card";
import {
  GUARDIAN_COURSE_SLUG,
  GUARDIAN_LEARNING_ROUTES,
} from "@/features/learning/constants";
import { useCourseOverview } from "@/features/learning/hooks/use-course-overview";

/**
 * Área do Responsável (RBAC do responsável — fase B): lista dos filhos
 * vinculados e autorizados à conta. Protegida em duas camadas
 * (`useRequireGuardian`); o backend também barra com 403.
 *
 * Traz a próxima aula da Formação de Pais como "próxima ação": a formação é
 * obrigatória, e o responsável precisa saber que ela existe sem ir procurar.
 */
export default function AreaResponsavelPage() {
  const isAuthorized = useRequireGuardian();
  const storedUser = useAuthStore((state) => state.user);

  const childrenQuery = useGuardianChildren();
  const courseQuery = useCourseOverview(GUARDIAN_COURSE_SLUG);
  const nextLesson = courseQuery.data?.next_lesson ?? null;

  return (
    <GuardianShell userName={storedUser?.name ?? "responsável"}>
      <PageHeader
        eyebrow="Área do responsável"
        title="Seus candidatos"
        description="Acompanhe o progresso na jornada — nunca a nota ou o desempenho."
      />

      {!isAuthorized || childrenQuery.isPending ? (
        <CardListSkeleton count={2} />
      ) : childrenQuery.isSuccess ? (
        <div className="flex flex-col gap-6">
          {/* Silencioso se a formação não carregar: a home é dos candidatos,
              e um erro secundário não pode esconder o conteúdo principal. */}
          {nextLesson ? (
            <ContinueLessonCard
              eyebrow="Sua formação"
              lesson={nextLesson}
              lessonHref={GUARDIAN_LEARNING_ROUTES.lesson}
            />
          ) : null}

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
