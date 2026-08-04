import {
  Bell,
  CalendarDays,
  Clock,
  Sparkles,
  Target,
  Trophy,
  type LucideIcon,
} from "lucide-react";

import type { NotificationCategory } from "@/features/notifications/types/notification.types";

interface CategoryStyle {
  icon: LucideIcon;
  /** Classes de cor do ícone/tile (fundo suave + texto de marca). */
  tone: string;
  label: string;
}

/**
 * Mapa de categoria → ícone, cor e rótulo. Explícito para dar identidade visual
 * a cada tipo de notificação sem importar a biblioteca de ícones inteira.
 */
const CATEGORY_STYLES: Record<NotificationCategory, CategoryStyle> = {
  sistema: { icon: Sparkles, tone: "bg-brand/10 text-brand", label: "Sistema" },
  eventos: {
    icon: CalendarDays,
    tone: "bg-brand-purple/10 text-brand-purple",
    label: "Eventos",
  },
  missoes: { icon: Target, tone: "bg-brand-green/10 text-brand-green", label: "Missões" },
  lembretes: {
    icon: Clock,
    tone: "bg-brand-orange/10 text-brand-orange",
    label: "Lembrete",
  },
  resultado: {
    icon: Trophy,
    tone: "bg-brand-orange/10 text-brand-orange",
    label: "Resultado",
  },
};

const FALLBACK: CategoryStyle = {
  icon: Bell,
  tone: "bg-muted text-muted-foreground",
  label: "Aviso",
};

export function resolveNotificationCategory(
  category: NotificationCategory,
): CategoryStyle {
  return CATEGORY_STYLES[category] ?? FALLBACK;
}
