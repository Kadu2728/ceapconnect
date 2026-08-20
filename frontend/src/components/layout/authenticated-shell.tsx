"use client";

import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { AuthenticatedNavbar } from "@/components/layout/authenticated-navbar";
import { BottomNav } from "@/components/layout/bottom-nav";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { cn } from "@/lib/utils";

// Montados em toda página autenticada, mas só entram em ação sob demanda (o
// candidato abre o chat; um level-up acontece) — carregá-los fora do bundle
// inicial tira framer-motion + a lógica de chat/confete do JS que toda página
// autenticada precisa baixar antes do primeiro paint (code splitting, Fase 4).
const AssistantWidget = dynamic(
  () =>
    import("@/features/assistant/components/assistant-widget").then(
      (mod) => mod.AssistantWidget,
    ),
  { ssr: false },
);
const LevelUpCelebration = dynamic(
  () =>
    import("@/features/level-up/components/level-up-celebration").then(
      (mod) => mod.LevelUpCelebration,
    ),
  { ssr: false },
);

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
