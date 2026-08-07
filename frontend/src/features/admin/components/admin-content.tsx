"use client";

import {
  Award,
  CalendarCheck,
  Gift,
  Sparkles,
  Target,
  TrendingUp,
  UserCheck,
  UserPlus,
  UserX,
  Users,
  Zap,
} from "lucide-react";

import { InterventionImpactCard } from "@/features/admin/components/intervention-impact-card";
import { KpiCard } from "@/features/admin/components/kpi-card";
import { LevelDistributionChart } from "@/features/admin/components/level-distribution-chart";
import { SignupsChart } from "@/features/admin/components/signups-chart";
import { TopRewardsList } from "@/features/admin/components/top-rewards-list";
import type { AdminOverview } from "@/features/admin/types/admin.types";

interface AdminContentProps {
  data: AdminOverview;
}

const nf = (value: number) => value.toLocaleString("pt-BR");

/** Cabeçalho de seção — cria hierarquia visual entre os blocos de métricas. */
function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      {children}
    </h2>
  );
}

/**
 * Composição do painel administrativo, em seções: acesso/engajamento dos alunos,
 * pulso da gamificação (XP, conquistas, recompensas) e visualizações (cadastros,
 * distribuição de níveis, ranking de recompensas).
 */
export function AdminContent({ data }: AdminContentProps) {
  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-3">
        <SectionHeading>Alunos & engajamento</SectionHeading>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            label="Total de alunos"
            value={nf(data.total_students)}
            icon={Users}
            accent="blue"
          />
          <KpiCard
            label="Já acessaram"
            value={nf(data.accessed)}
            hint={`${data.engagement_rate}% de engajamento`}
            icon={UserCheck}
            accent="green"
          />
          <KpiCard
            label="Nunca acessaram"
            value={nf(data.never_accessed)}
            hint="Cadastraram mas não entraram"
            icon={UserX}
            accent="orange"
          />
          <KpiCard
            label="Ativos (7 dias)"
            value={nf(data.active_7d)}
            hint={`${nf(data.active_24h)} nas últimas 24h`}
            icon={Sparkles}
            accent="purple"
          />
        </div>
      </section>

      <section className="flex flex-col gap-3">
        <SectionHeading>Pulso da gamificação</SectionHeading>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            label="Missões concluídas"
            value={nf(data.missions_completed)}
            icon={Target}
            accent="green"
          />
          <KpiCard
            label="Conquistas desbloqueadas"
            value={nf(data.achievements_unlocked)}
            icon={Award}
            accent="orange"
          />
          <KpiCard
            label="XP distribuído"
            value={nf(data.total_xp)}
            hint={`${nf(data.avg_xp)} XP por aluno em média`}
            icon={Zap}
            accent="purple"
          />
          <KpiCard
            label="Recompensas resgatadas"
            value={nf(data.rewards_redeemed)}
            hint={`${nf(data.rewards_pending)} pendente(s) · ${nf(data.rewards_fulfilled)} entregue(s)`}
            icon={Gift}
            accent="blue"
          />
        </div>
      </section>

      <section className="flex flex-col gap-3">
        <SectionHeading>Console de risco</SectionHeading>
        <InterventionImpactCard data={data.intervention_impact} />
      </section>

      <section className="flex flex-col gap-3">
        <SectionHeading>Visão da plataforma</SectionHeading>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <SignupsChart data={data.signups_daily} />
          </div>
          <div className="flex flex-col gap-4">
            <KpiCard
              label="Novos alunos (30 dias)"
              value={nf(data.new_30d)}
              hint={`${nf(data.new_7d)} nos últimos 7 dias`}
              icon={UserPlus}
              accent="blue"
            />
            <KpiCard
              label="Inscrições em eventos"
              value={nf(data.event_registrations)}
              icon={CalendarCheck}
              accent="green"
            />
            <KpiCard
              label="Base engajada"
              value={`${data.engagement_rate}%`}
              hint="Alunos que já acessaram a plataforma"
              icon={TrendingUp}
              accent="purple"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <LevelDistributionChart data={data.level_distribution} />
          <TopRewardsList data={data.top_rewards} />
        </div>
      </section>
    </div>
  );
}
