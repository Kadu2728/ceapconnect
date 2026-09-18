"use client";

import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { CourseOverviewView } from "@/features/learning/components/course-overview-view";
import {
  CANDIDATE_COURSE_SLUG,
  CANDIDATE_LEARNING_ROUTES,
} from "@/features/learning/constants";

/**
 * Videoaulas do candidato — o curso de preparação para a prova, na mesma
 * casca das outras telas do aluno (navbar + bottom nav). O corpo é o
 * `CourseOverviewView` compartilhado com a Formação de Pais; a autorização
 * por público acontece no backend (um responsável recebe 403 aqui).
 */
export default function AulasPage() {
  const isAuthorized = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const dashboardQuery = useDashboard();

  const displayName =
    dashboardQuery.data?.greeting_name ?? storedUser?.name ?? "candidato";
  const unreadNotificationsCount = dashboardQuery.data?.unread_notifications_count ?? 0;

  return (
    <AuthenticatedShell
      userName={displayName}
      unreadNotificationsCount={unreadNotificationsCount}
    >
      <PageHeader
        eyebrow="Preparação"
        title="Videoaulas"
        description="Aulas curtas para você entender a prova e chegar preparado no dia. Assista no seu ritmo — seu progresso fica salvo."
      />

      <CourseOverviewView
        slug={CANDIDATE_COURSE_SLUG}
        routes={CANDIDATE_LEARNING_ROUTES}
        ready={isAuthorized}
        continueEyebrow="Continue sua preparação"
      />
    </AuthenticatedShell>
  );
}
