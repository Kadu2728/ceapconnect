import type { Pillar, PillarAccent } from "@/features/landing/types/pillar";
import { cn } from "@/lib/utils";

/**
 * Mapa de cores de marca por pilar. Classes são literais (não interpoladas)
 * para que o Tailwind as detecte no build.
 */
const ACCENT_STYLES: Record<
  PillarAccent,
  { tile: string; border: string; shadow: string }
> = {
  blue: {
    tile: "from-brand/15 to-brand/5 text-brand",
    border: "hover:border-brand/40",
    shadow: "hover:shadow-brand/10",
  },
  green: {
    tile: "from-brand-green/15 to-brand-green/5 text-brand-green",
    border: "hover:border-brand-green/40",
    shadow: "hover:shadow-brand-green/10",
  },
  orange: {
    tile: "from-brand-orange/15 to-brand-orange/5 text-brand-orange",
    border: "hover:border-brand-orange/40",
    shadow: "hover:shadow-brand-orange/10",
  },
  purple: {
    tile: "from-brand-purple/15 to-brand-purple/5 text-brand-purple",
    border: "hover:border-brand-purple/40",
    shadow: "hover:shadow-brand-purple/10",
  },
  cyan: {
    tile: "from-brand-2/20 to-brand-2/5 text-brand-2",
    border: "hover:border-brand-2/40",
    shadow: "hover:shadow-brand-2/10",
  },
};

interface PillarCardProps {
  pillar: Pillar;
}

/**
 * Card de um pilar do produto (Jornada, Missões, Conquistas, Eventos,
 * Notificações). Cada pilar carrega uma cor do cluster de marca do CEAP; o
 * hover eleva o card e revela um contorno na cor do pilar — microinteração
 * elegante e colorida, nunca infantil (PROJECT_OVERVIEW.md).
 */
export function PillarCard({ pillar }: PillarCardProps) {
  const Icon = pillar.icon;
  const accent = ACCENT_STYLES[pillar.accent];

  return (
    <div
      className={cn(
        "group h-full rounded-2xl border border-border/70 bg-card p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg",
        accent.border,
        accent.shadow,
      )}
    >
      <span
        className={cn(
          "mb-4 flex size-11 items-center justify-center rounded-xl bg-gradient-to-br transition-transform duration-300 group-hover:scale-105",
          accent.tile,
        )}
      >
        <Icon className="size-5" aria-hidden="true" />
      </span>

      <h3 className="font-semibold text-foreground">{pillar.title}</h3>
      <p className="mt-1.5 text-sm text-muted-foreground">{pillar.description}</p>
    </div>
  );
}
