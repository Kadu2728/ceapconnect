import { Award, Gift, Target, Zap, type LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { ProfileStats as Stats } from "@/features/profile/types/profile.types";
import { cn } from "@/lib/utils";

interface ProfileStatsProps {
  stats: Stats;
}

interface StatTile {
  label: string;
  value: string;
  hint?: string;
  icon: LucideIcon;
  tone: string;
}

/**
 * Grade de estatísticas do candidato: XP/nível, missões concluídas, conquistas
 * e recompensas resgatadas — o "cartão de visitas" da jornada, num relance.
 */
export function ProfileStats({ stats }: ProfileStatsProps) {
  const { level } = stats;
  const nf = (value: number) => value.toLocaleString("pt-BR");

  const tiles: StatTile[] = [
    {
      label: "XP acumulado",
      value: nf(level.xp_total),
      hint: level.is_max_level
        ? "Nível máximo"
        : `Faltam ${nf(level.xp_to_next ?? 0)} XP p/ o Nível ${level.level + 1}`,
      icon: Zap,
      tone: "bg-brand-purple/10 text-brand-purple",
    },
    {
      label: "Missões concluídas",
      value: nf(stats.missions_completed),
      icon: Target,
      tone: "bg-brand-green/10 text-brand-green",
    },
    {
      label: "Conquistas",
      value: nf(stats.achievements_unlocked),
      icon: Award,
      tone: "bg-brand-orange/10 text-brand-orange",
    },
    {
      label: "Recompensas",
      value: nf(stats.rewards_redeemed),
      hint: "Resgatadas",
      icon: Gift,
      tone: "bg-brand/10 text-brand",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {tiles.map((tile) => (
        <Card key={tile.label} className="gap-3">
          <div className="flex items-start justify-between gap-3 px-6">
            <div className="min-w-0">
              <p className="text-sm text-muted-foreground">{tile.label}</p>
              <p className="mt-1 text-2xl font-bold tracking-tight tabular-nums">
                {tile.value}
              </p>
              {tile.hint ? (
                <p className="mt-1 text-xs text-muted-foreground">{tile.hint}</p>
              ) : null}
            </div>
            <span
              className={cn(
                "flex size-10 shrink-0 items-center justify-center rounded-xl",
                tile.tone,
              )}
            >
              <tile.icon className="size-5" aria-hidden="true" />
            </span>
          </div>
        </Card>
      ))}
    </div>
  );
}
