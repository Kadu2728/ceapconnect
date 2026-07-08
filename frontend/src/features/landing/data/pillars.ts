import { Award, Bell, CalendarDays, Route, Target } from "lucide-react";

import type { Pillar } from "@/features/landing/types/pillar";

/**
 * Pilares do produto (USER_FLOW.md): Jornada, Missões, Conquistas, Eventos e
 * Notificações — os mesmos módulos que compõem o Dashboard, apresentados aqui
 * de forma educativa. Dados isolados da UI para reuso e teste.
 */
export const PILLARS: Pillar[] = [
  {
    icon: Route,
    title: "Jornada",
    description:
      "Veja exatamente onde você está e o que vem a seguir, do cadastro ao resultado.",
    accent: "blue",
  },
  {
    icon: Target,
    title: "Missões",
    description:
      "Pequenas ações guiadas que mantêm você preparado e engajado a cada semana.",
    accent: "green",
  },
  {
    icon: Award,
    title: "Conquistas",
    description: "Reconhecimento visível para cada etapa concluída, do jeito certo.",
    accent: "orange",
  },
  {
    icon: CalendarDays,
    title: "Eventos",
    description:
      "Inscreva-se em eventos e receba tudo o que precisa saber, na hora certa.",
    accent: "purple",
  },
  {
    icon: Bell,
    title: "Notificações",
    description:
      "Prazos e atualizações centralizados, para você nunca mais perder uma data.",
    accent: "cyan",
  },
];
