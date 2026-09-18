"use client";

import { useParams } from "next/navigation";

import { GuardianShell } from "@/components/layout/guardian-shell";
import { useRequireGuardian } from "@/features/auth/hooks/use-require-guardian";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { LessonView } from "@/features/learning/components/lesson-view";
import { GUARDIAN_LEARNING_ROUTES } from "@/features/learning/constants";

/** Aula da Formação de Pais — casca do responsável em volta de `LessonView`. */
export default function AulaPage() {
  const params = useParams<{ lessonId: string }>();
  const isAuthorized = useRequireGuardian();
  const storedUser = useAuthStore((state) => state.user);

  return (
    <GuardianShell userName={storedUser?.name ?? "responsável"}>
      <LessonView
        lessonId={params.lessonId}
        routes={GUARDIAN_LEARNING_ROUTES}
        ready={isAuthorized}
        courseLabel="Formação de Pais"
      />
    </GuardianShell>
  );
}
