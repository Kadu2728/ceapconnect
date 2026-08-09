"use client";

import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { AuthenticatedNavbar } from "@/components/layout/authenticated-navbar";
import { BottomNav } from "@/components/layout/bottom-nav";
import { AssistantWidget } from "@/features/assistant/components/assistant-widget";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { LevelUpCelebration } from "@/features/level-up/components/level-up-celebration";
import { cn } from "@/lib/utils";

interface AuthenticatedShellProps {
  userName: string;
  unreadNotificationsCount: number;
  children: ReactNode;
  className?: string;
}

/**
 * Casca compartilhada de toda página autenticada: navbar + bottom navigation
 * (mobile) + logout, com o container e o respiro inferior (para não colidir
 * com a `BottomNav`) padronizados. As páginas cuidam apenas do próprio guard de
 * sessão e do conteúdo — a moldura vive aqui, sem duplicação.
 */
export function AuthenticatedShell({
  userName,
  unreadNotificationsCount,
  children,
  className,
}: AuthenticatedShellProps) {
  const router = useRouter();
  const clearSession = useAuthStore((state) => state.clearSession);

  const handleLogout = () => {
    clearSession();
    router.push("/");
  };

  return (
    <div className="flex min-h-svh flex-col bg-muted/30">
      {/* Primeiro foco tabulável da página: sem ele, chegar ao conteúdo pelo
          teclado exige passar por toda a navegação em cada tela. */}
      <a
        href="#conteudo"
        className="sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground"
      >
        Pular para o conteúdo
      </a>

      <AuthenticatedNavbar
        userName={userName}
        unreadNotificationsCount={unreadNotificationsCount}
        onLogout={handleLogout}
      />

      <main
        id="conteudo"
        tabIndex={-1}
        className={cn(
          "mx-auto w-full max-w-6xl flex-1 px-4 py-8 pb-28 outline-none sm:px-6 lg:px-8 lg:py-12 md:pb-12",
          className,
        )}
      >
        {children}
      </main>

      <BottomNav />
      <AssistantWidget />
      <LevelUpCelebration />
    </div>
  );
}
