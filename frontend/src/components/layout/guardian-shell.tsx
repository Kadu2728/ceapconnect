"use client";

import { LogOut } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { CeapLogo } from "@/components/brand/ceap-logo";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { APP_CONTAINER_CLASS } from "@/lib/layout";
import { cn } from "@/lib/utils";

interface GuardianShellProps {
  userName: string;
  children: ReactNode;
  className?: string;
}

/**
 * Casca dedicada da Área do Responsável — deliberadamente separada de
 * `AuthenticatedShell` (usada pelo candidato): aquela carrega navegação,
 * assistente de IA e celebração de level-up específicos do candidato
 * (Missões, Simulados, Recompensas etc.), nenhum dos quais faz sentido para
 * quem só acompanha a jornada de fora. Reaproveita só o que é genuinamente
 * comum (logo, tema, container) — não a navbar inteira.
 */
export function GuardianShell({ userName, children, className }: GuardianShellProps) {
  const router = useRouter();
  const clearSession = useAuthStore((state) => state.clearSession);

  const handleLogout = () => {
    clearSession();
    router.push("/");
  };

  return (
    <div className="flex min-h-svh flex-col bg-muted/30">
      <a
        href="#conteudo"
        className="sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground"
      >
        Pular para o conteúdo
      </a>

      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
        <div
          className={cn(
            APP_CONTAINER_CLASS,
            "flex h-16 items-center justify-between gap-4",
          )}
        >
          <Link href="/area-responsavel" aria-label="CEAP Connect — Área do responsável">
            <CeapLogo wordmarkClassName="hidden min-[360px]:inline lg:inline" />
          </Link>

          <div className="flex items-center gap-2 sm:gap-3">
            <span className="hidden max-w-[10rem] truncate text-sm font-medium text-muted-foreground sm:inline">
              {userName}
            </span>
            <ThemeToggle />
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              aria-label="Sair da conta"
              className="text-muted-foreground hover:text-foreground"
            >
              <LogOut className="size-4" aria-hidden="true" />
            </Button>
          </div>
        </div>
      </header>

      <main
        id="conteudo"
        tabIndex={-1}
        className={cn(
          "mx-auto w-full max-w-4xl flex-1 px-4 py-8 outline-none sm:px-6 lg:px-8 lg:py-12",
          className,
        )}
      >
        {children}
      </main>
    </div>
  );
}
