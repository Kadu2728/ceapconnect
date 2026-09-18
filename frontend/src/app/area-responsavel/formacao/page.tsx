"use client";

import { GuardianShell } from "@/components/layout/guardian-shell";
import { PageHeader } from "@/components/layout/page-header";
import { useRequireGuardian } from "@/features/auth/hooks/use-require-guardian";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { CourseOverviewView } from "@/features/learning/components/course-overview-view";
import {
  GUARDIAN_COURSE_SLUG,
  GUARDIAN_LEARNING_ROUTES,
} from "@/features/learning/constants";

/**
 * Formação de Pais — dashboard do curso do responsável. A página só decide
 * casca e guard; o corpo (`CourseOverviewView`) é o mesmo da preparação do
 * candidato.
 */
export default function FormacaoPage() {
  const isAuthorized = useRequireGuardian();
  const storedUser = useAuthStore((state) => state.user);

  return (
    <GuardianShell userName={storedUser?.name ?? "responsável"}>
      <PageHeader
        eyebrow="Área do responsável"
        title="Formação de Pais"
        description="Acompanhe sua formação, assista às aulas e avance pelas etapas do curso."
      />

      <CourseOverviewView
        slug={GUARDIAN_COURSE_SLUG}
        routes={GUARDIAN_LEARNING_ROUTES}
        ready={isAuthorized}
        continueEyebrow="Continue sua formação"
      />
    </GuardianShell>
  );
}
