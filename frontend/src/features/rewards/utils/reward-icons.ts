import {
  Award,
  BadgeCheck,
  Clapperboard,
  Cloud,
  Code,
  GraduationCap,
  Languages,
  Laptop,
  Monitor,
  Network,
  Palette,
  Sparkles,
  Table,
  type LucideIcon,
} from "lucide-react";

/**
 * Mapa de nomes de ícone da API (ex.: `"cloud"`) para o componente
 * `lucide-react` correspondente. Explícito de propósito — indexar a biblioteca
 * por nome dinâmico importaria tudo e mataria o tree-shaking.
 */
const REWARD_ICON_MAP: Record<string, LucideIcon> = {
  cloud: Cloud,
  monitor: Monitor,
  laptop: Laptop,
  clapperboard: Clapperboard,
  network: Network,
  table: Table,
  languages: Languages,
  "badge-check": BadgeCheck,
  "graduation-cap": GraduationCap,
  code: Code,
  palette: Palette,
  sparkles: Sparkles,
  award: Award,
};

/** Ícone genérico para nomes não mapeados. */
const FALLBACK_ICON: LucideIcon = GraduationCap;

export function resolveRewardIcon(iconName: string): LucideIcon {
  const normalized = iconName.trim().toLowerCase();
  return REWARD_ICON_MAP[normalized] ?? FALLBACK_ICON;
}
