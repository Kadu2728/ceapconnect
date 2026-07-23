import type { LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type KpiAccent = "blue" | "green" | "orange" | "purple";

const ACCENT_STYLES: Record<KpiAccent, string> = {
  blue: "bg-brand/10 text-brand",
  green: "bg-brand-green/10 text-brand-green",
  orange: "bg-brand-orange/10 text-brand-orange",
  purple: "bg-brand-purple/10 text-brand-purple",
};

interface KpiCardProps {
  label: string;
  value: string;
  hint?: string;
  icon: LucideIcon;
  accent?: KpiAccent;
}

/**
 * Cartão de indicador (KPI) do painel admin: rótulo, valor grande em números
 * tabulares e um ícone na cor de marca. Reutilizado por todas as métricas.
 */
export function KpiCard({
  label,
  value,
  hint,
  icon: Icon,
  accent = "blue",
}: KpiCardProps) {
  return (
    <Card className="gap-3 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between gap-3 px-6">
        <div className="min-w-0">
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="mt-1 text-3xl font-bold tracking-tight tabular-nums">{value}</p>
          {hint ? <p className="mt-1 text-xs text-muted-foreground">{hint}</p> : null}
        </div>
        <span
          className={cn(
            "flex size-10 shrink-0 items-center justify-center rounded-xl",
            ACCENT_STYLES[accent],
          )}
        >
          <Icon className="size-5" aria-hidden="true" />
        </span>
      </div>
    </Card>
  );
}
