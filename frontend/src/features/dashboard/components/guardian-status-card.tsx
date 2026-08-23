import { HeartHandshake } from "lucide-react";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import type { DashboardGuardianStatus } from "@/features/dashboard/types/dashboard.types";

interface GuardianStatusCardProps {
  status: DashboardGuardianStatus;
}

/**
 * Incentiva o candidato a "puxar o responsável" (mentoria do CEAP: ausência
 * do responsável na formação obrigatória é fator de evasão de primeira
 * ordem — se ele não participa, o candidato perde a vaga). Mostra só o
 * status da jornada do responsável, nunca o score de risco do candidato,
 * que ele jamais vê.
 */
export function GuardianStatusCard({ status }: GuardianStatusCardProps) {
  if (status.training_attended) {
    return (
      <DashboardCard className="flex items-center gap-4">
        <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-brand-green/10 text-brand-green">
          <HeartHandshake className="size-6" aria-hidden="true" />
        </span>
        <div>
          <h2 className="text-sm font-semibold">Responsável na jornada</h2>
          <p className="text-sm text-muted-foreground">
            Seu responsável já concluiu a formação obrigatória. 💚
          </p>
        </div>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard className="flex items-center gap-4">
      <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-warning/10 text-warning">
        <HeartHandshake className="size-6" aria-hidden="true" />
      </span>
      <div>
        <h2 className="text-sm font-semibold">Chame seu responsável para a formação</h2>
        <p className="text-sm text-muted-foreground">
          {status.has_guardian
            ? "A participação dele na formação obrigatória é uma etapa do seu processo seletivo — sem ela, você pode perder a vaga."
            : "Cadastre o contato do seu responsável no Perfil e chame ele para a formação obrigatória — sem ela, você pode perder a vaga."}
        </p>
      </div>
    </DashboardCard>
  );
}
