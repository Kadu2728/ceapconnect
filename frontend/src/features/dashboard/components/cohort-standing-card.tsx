import { Users } from "lucide-react";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import type { DashboardCohortStanding } from "@/features/dashboard/types/dashboard.types";

interface CohortStandingCardProps {
  standing: DashboardCohortStanding | null;
}

/**
 * Situa o candidato na própria turma sem nenhum ranking nominal (EPIC 20):
 * só a faixa de engajamento e o tamanho da coorte. `null` (turma pequena
 * demais para ser anônima, sem coorte ou sem XP) simplesmente não renderiza —
 * comparar nesses casos não informa nada e pode desmotivar.
 */
export function CohortStandingCard({ standing }: CohortStandingCardProps) {
  if (!standing) return null;

  return (
    <DashboardCard className="flex items-center gap-4">
      <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-brand-green/10 text-brand-green">
        <Users className="size-6" aria-hidden="true" />
      </span>
      <div>
        <h2 className="text-sm font-semibold">
          {standing.top_percent !== null
            ? `Top ${standing.top_percent}% da sua turma`
            : "Sua turma"}
        </h2>
        <p className="text-sm text-muted-foreground">
          {standing.message} Turma com {standing.cohort_size} candidatos.
        </p>
      </div>
    </DashboardCard>
  );
}
