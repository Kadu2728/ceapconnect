"use client";

import { Bell, LogOut } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { CeapLogo } from "@/components/brand/ceap-logo";
import { visibleNavItems } from "@/components/layout/authenticated-nav-items";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { APP_CONTAINER_CLASS } from "@/lib/layout";
import { getInitials } from "@/lib/text";
import { cn } from "@/lib/utils";

interface AuthenticatedNavbarProps {
  userName: string;
  unreadNotificationsCount: number;
  onLogout: () => void;
}

/**
 * Navbar da área autenticada (Dashboard, Missões, Conquistas, Eventos).
 *
 * A navegação principal aparece inline no desktop; no mobile ela vive na
 * `BottomNav` (padrão de app para o público majoritariamente mobile). O que é
 * comum com a Landing (container, `ThemeToggle`, `CeapLogo`) é reutilizado,
 * nunca duplicado.
 */
export function AuthenticatedNavbar({
  userName,
  unreadNotificationsCount,
  onLogout,
}: AuthenticatedNavbarProps) {
  const pathname = usePathname();
  const isAdmin = useAuthStore((state) => state.user?.is_admin ?? false);
  const navItems = visibleNavItems(isAdmin);
  const initials = getInitials(userName);
  const hasUnread = unreadNotificationsCount > 0;

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
      <div
        className={cn(
          APP_CONTAINER_CLASS,
          "flex h-16 items-center justify-between gap-4",
        )}
      >
        <Link href="/dashboard" aria-label="CEAP Connect — início" className="shrink-0">
          <CeapLogo wordmarkClassName="hidden min-[360px]:inline lg:inline" />
        </Link>

        <nav
          aria-label="Navegação principal"
          className="hidden items-center gap-1 md:flex"
        >
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-brand/10 text-brand"
                    : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            href="/notificacoes"
            aria-label={
              hasUnread
                ? `Notificações — ${unreadNotificationsCount} não lidas`
                : "Notificações"
            }
            aria-current={pathname === "/notificacoes" ? "page" : undefined}
            className={cn(
              "relative inline-flex size-9 items-center justify-center rounded-md transition-colors hover:bg-accent/60 hover:text-foreground",
              pathname === "/notificacoes" ? "text-brand" : "text-muted-foreground",
            )}
          >
            <Bell className="size-4" aria-hidden="true" />
            {hasUnread ? (
              <span
                aria-hidden="true"
                className="absolute top-1 right-1 flex size-4 items-center justify-center rounded-full bg-destructive text-[10px] font-semibold text-white"
              >
                {unreadNotificationsCount > 9 ? "9+" : unreadNotificationsCount}
              </span>
            ) : null}
          </Link>

          <ThemeToggle />

          <div className="flex items-center gap-2 border-l border-border/60 pl-2 sm:pl-3">
            <Link
              href="/perfil"
              aria-label="Meu perfil"
              aria-current={pathname === "/perfil" ? "page" : undefined}
              className="flex items-center gap-2 rounded-full transition-opacity hover:opacity-80"
            >
              <span
                aria-hidden="true"
                className="flex size-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground"
              >
                {initials}
              </span>
              <span className="hidden max-w-[9rem] truncate text-sm font-medium lg:inline">
                {userName}
              </span>
            </Link>

            <Button
              variant="ghost"
              size="icon"
              onClick={onLogout}
              aria-label="Sair da conta"
              className="text-muted-foreground hover:text-foreground"
            >
              <LogOut className="size-4" aria-hidden="true" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
