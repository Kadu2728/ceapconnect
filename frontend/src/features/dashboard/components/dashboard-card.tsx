import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface DashboardCardProps {
  children: ReactNode;
  className?: string;
}

/**
 * Superfície de cartão padrão do Dashboard — mesma linguagem visual usada na
 * Landing Page e no placeholder da EPIC 02 (`rounded-2xl border bg-card
 * shadow-sm`), mantendo consistência entre a área pública e a autenticada
 * (DESIGN_SYSTEM.md: "todos devem seguir o mesmo padrão visual").
 */
export function DashboardCard({ children, className }: DashboardCardProps) {
  return (
    <div className={cn("rounded-2xl border bg-card p-6 shadow-sm sm:p-8", className)}>
      {children}
    </div>
  );
}
