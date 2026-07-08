import {
  CalendarDays,
  LayoutDashboard,
  Target,
  Trophy,
  type LucideIcon,
} from "lucide-react";

export interface AuthNavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

/**
 * Itens de navegação da área autenticada, compartilhados entre a navbar
 * (desktop) e a bottom navigation (mobile) — fonte única de verdade para não
 * divergir entre as duas.
 */
export const AUTH_NAV_ITEMS: AuthNavItem[] = [
  { href: "/dashboard", label: "Início", icon: LayoutDashboard },
  { href: "/missoes", label: "Missões", icon: Target },
  { href: "/conquistas", label: "Conquistas", icon: Trophy },
  { href: "/eventos", label: "Eventos", icon: CalendarDays },
];
