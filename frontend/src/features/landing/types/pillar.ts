import type { LucideIcon } from "lucide-react";

/**
 * Cor de marca aplicada a um pilar (deriva do cluster de círculos do logo do
 * CEAP: azul, verde, roxo, laranja e ciano). Mantida como união fechada para
 * que o Tailwind veja classes estáticas em `PillarCard`.
 */
export type PillarAccent = "blue" | "green" | "orange" | "purple" | "cyan";

/**
 * Um dos pilares do produto exibidos na Landing Page (Jornada, Missões,
 * Conquistas, Eventos, Notificações — ver USER_FLOW.md).
 */
export interface Pillar {
  icon: LucideIcon;
  title: string;
  description: string;
  accent: PillarAccent;
}
