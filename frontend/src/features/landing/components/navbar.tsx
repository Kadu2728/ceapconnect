import Link from "next/link";

import { CeapLogo } from "@/components/brand/ceap-logo";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Button } from "@/components/ui/button";
import { MobileMenu } from "@/features/landing/components/mobile-menu";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import { cn } from "@/lib/utils";

type NavAuthLink = "login" | "cadastro" | "none";

const AUTH_LINK_CONFIG: Record<
  Exclude<NavAuthLink, "none">,
  { href: string; label: string }
> = {
  login: { href: "/login", label: "Entrar" },
  cadastro: { href: "/cadastro", label: "Criar conta" },
};

const SECTION_LINKS = [
  { href: "/#jornada", label: "Como funciona" },
  { href: "/#cursos", label: "Cursos" },
  { href: "/#ingresso", label: "Processo seletivo" },
];

interface NavbarProps {
  /**
   * Controla o link contextual de autenticação. Nunca deve apontar para a
   * página atual (ex.: em `/login`, o correto é "Criar conta").
   */
  authLink?: NavAuthLink;
  /**
   * Exibe a navegação por âncoras das seções — apenas na Landing Page, onde
   * essas seções existem. Em `/login` e `/cadastro` fica desativado.
   */
  showSectionNav?: boolean;
}

/**
 * Navbar sticky da Landing Page e das páginas públicas (cadastro/login).
 *
 * Server Component — a única interatividade real (alternar tema) vive isolada
 * em `ThemeToggle`. Fundo translúcido com blur reforça a sensação de produto
 * moderno sem competir com o conteúdo ao rolar.
 */
export function Navbar({ authLink = "login", showSectionNav = false }: NavbarProps) {
  const auth = authLink === "none" ? null : AUTH_LINK_CONFIG[authLink];

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/70 backdrop-blur-xl supports-[backdrop-filter]:bg-background/55">
      <div
        className={cn(
          LANDING_CONTAINER_CLASS,
          "flex h-16 items-center justify-between gap-4",
        )}
      >
        <Link href="/" aria-label="CEAP Connect — início" className="shrink-0">
          {/* Em telas muito estreitas (&lt;360px) mostramos só a marca gráfica
              para a navbar nunca transbordar. */}
          <CeapLogo wordmarkClassName="hidden min-[360px]:inline" />
        </Link>

        {showSectionNav ? (
          <nav aria-label="Seções" className="hidden items-center gap-1 md:flex">
            {SECTION_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        ) : null}

        <div className="flex items-center gap-2 sm:gap-3">
          <ThemeToggle />

          {showSectionNav ? (
            <>
              <Button variant="ghost" size="sm" asChild className="hidden md:inline-flex">
                <Link href="/login">Entrar</Link>
              </Button>
              <Button size="sm" asChild className="hidden min-[360px]:inline-flex">
                <Link href="/cadastro">Criar conta</Link>
              </Button>
              <MobileMenu links={SECTION_LINKS} />
            </>
          ) : auth ? (
            <Button variant="ghost" size="sm" asChild>
              <Link href={auth.href}>{auth.label}</Link>
            </Button>
          ) : null}
        </div>
      </div>
    </header>
  );
}
