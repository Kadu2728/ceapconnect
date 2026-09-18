"use client";

import { useParams } from "next/navigation";

import { AuthenticatedShell } from "@/components/layout/authenticated-shell";
import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { LessonView } from "@/features/learning/components/lesson-view";
import { CANDIDATE_LEARNING_ROUTES } from "@/features/learning/constants";

/** Aula do candidato — casca do aluno em volta de `LessonView`. */
export default function AulaDoCandidatoPage() {
  const params = useParams<{ lessonId: string }>();
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
      <LessonView
        lessonId={params.lessonId}
        routes={CANDIDATE_LEARNING_ROUTES}
        ready={isAuthorized}
        courseLabel="Videoaulas"
      />
    </AuthenticatedShell>
  );
}
