import {
  Award,
  BadgeCheck,
  BookOpen,
  Crown,
  Flag,
  Flame,
  Gem,
  Medal,
  Rocket,
  Shield,
  Sparkles,
  Star,
  Target,
  Trophy,
  Zap,
  type LucideIcon,
} from "lucide-react";

/**
 * Mapa de nomes de ícone retornados pela API (ex.: `"trophy"`) para o
 * componente `lucide-react` correspondente.
 *
 * Mantido pequeno e explícito de propósito: indexar `lucide-react` por nome
 * dinâmico exigiria importar a biblioteca inteira, perdendo tree-shaking dos
 * ícones não usados.
 */
const ACHIEVEMENT_ICON_MAP: Record<string, LucideIcon> = {
  trophy: Trophy,
  star: Star,
  award: Award,
  medal: Medal,
  crown: Crown,
  target: Target,
  flag: Flag,
  flame: Flame,
  zap: Zap,
  gem: Gem,
  rocket: Rocket,
  shield: Shield,
  sparkles: Sparkles,
  "book-open": BookOpen,
  "badge-check": BadgeCheck,
};

/** Ícone genérico exibido quando a API retorna um nome não mapeado. */
const FALLBACK_ICON: LucideIcon = Award;

export function resolveAchievementIcon(iconName: string): LucideIcon {
  const normalized = iconName.trim().toLowerCase();
  return ACHIEVEMENT_ICON_MAP[normalized] ?? FALLBACK_ICON;
}
