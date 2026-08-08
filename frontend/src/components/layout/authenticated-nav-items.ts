import {
  AlertTriangle,
  CalendarDays,
  FileText,
  Gift,
  LayoutDashboard,
  ShieldCheck,
  Target,
  Trophy,
  type LucideIcon,
} from "lucide-react";

import type { UserRole } from "@/features/auth/types/auth.types";

export interface AuthNavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  /** Item visível apenas para administradores (ex.: painel admin). */
  adminOnly?: boolean;
  /** Item visível para coordenadores e administradores (ex.: Console de Intervenção). */
  staffOnly?: boolean;
}

/**
 * Itens de navegação da área autenticada, compartilhados entre a navbar
 * (desktop) e a bottom navigation (mobile) — fonte única de verdade para não
 * divergir entre as duas.
 */
export const AUTH_NAV_ITEMS: AuthNavItem[] = [
  { href: "/dashboard", label: "Início", icon: LayoutDashboard },
  { href: "/documentos", label: "Documentos", icon: FileText },
  { href: "/missoes", label: "Missões", icon: Target },
  { href: "/conquistas", label: "Conquistas", icon: Trophy },
  { href: "/recompensas", label: "Recompensas", icon: Gift },
  { href: "/eventos", label: "Eventos", icon: CalendarDays },
  { href: "/risco", label: "Risco", icon: AlertTriangle, staffOnly: true },
  { href: "/admin", label: "Admin", icon: ShieldCheck, adminOnly: true },
];

interface VisibilityContext {
  isAdmin: boolean;
  role: UserRole;
}

/**
 * Filtra os itens conforme o papel do usuário: admin vê tudo, coordenador vê
 * os itens `staffOnly` (Console de Intervenção) mas não `adminOnly` (painel
 * de métricas gerais), candidato não vê nenhum dos dois.
 *
 * Esta é só a visibilidade da **navegação** — o controle de acesso real
 * acontece no backend (RBAC com escopo de coorte, EPIC 14); esconder o item
 * aqui é UX, nunca segurança.
 */
export function visibleNavItems({ isAdmin, role }: VisibilityContext): AuthNavItem[] {
  const isStaff = isAdmin || role === "coordinator";
  return AUTH_NAV_ITEMS.filter((item) => {
    if (item.adminOnly) return isAdmin;
    if (item.staffOnly) return isStaff;
    return true;
  });
}
