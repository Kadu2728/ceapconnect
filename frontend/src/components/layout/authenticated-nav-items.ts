import {
  CalendarDays,
  Gift,
  LayoutDashboard,
  ShieldCheck,
  Target,
  Trophy,
  type LucideIcon,
} from "lucide-react";

export interface AuthNavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  /** Item visível apenas para administradores (ex.: painel admin). */
  adminOnly?: boolean;
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
  { href: "/recompensas", label: "Recompensas", icon: Gift },
  { href: "/eventos", label: "Eventos", icon: CalendarDays },
  { href: "/admin", label: "Admin", icon: ShieldCheck, adminOnly: true },
];

/** Filtra os itens conforme o papel do usuário (admin vê o item do painel). */
export function visibleNavItems(isAdmin: boolean): AuthNavItem[] {
  return AUTH_NAV_ITEMS.filter((item) => !item.adminOnly || isAdmin);
}
