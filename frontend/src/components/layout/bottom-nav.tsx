"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { visibleNavItems } from "@/components/layout/authenticated-nav-items";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { cn } from "@/lib/utils";

/**
 * Navegação inferior fixa da área autenticada, exibida apenas no mobile
 * (`md:hidden`). Padrão de app nativo para o público majoritariamente mobile
 * (16–25 anos): destinos de topo sempre a um toque, respeitando a safe-area
 * inferior. Máximo de 5 itens (regra `bottom-nav-limit`).
 *
 * Quando há mais destinos que o limite (ex.: admin com o item "Admin"), o
 * rodapé mobile mostra apenas os 5 primeiros — o painel Admin é desktop-first e
 * segue acessível pela navbar em telas maiores.
 */
const BOTTOM_NAV_LIMIT = 5;

export function BottomNav() {
  const pathname = usePathname();
  const isAdmin = useAuthStore((state) => state.user?.is_admin ?? false);
  const role = useAuthStore((state) => state.user?.role ?? "candidate");
  const navItems = visibleNavItems({ isAdmin, role }).slice(0, BOTTOM_NAV_LIMIT);

  return (
    <nav
      aria-label="Navegação principal"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-border/60 bg-background/90 pb-[env(safe-area-inset-bottom)] backdrop-blur-xl md:hidden"
    >
      <ul className="mx-auto flex max-w-md items-stretch justify-around">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <li key={item.href} className="flex-1">
              <Link
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "flex flex-col items-center gap-1 px-1 py-2.5 text-[11px] font-medium transition-colors",
                  isActive ? "text-brand" : "text-muted-foreground hover:text-foreground",
                )}
              >
                <Icon className="size-5" aria-hidden="true" />
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
