import { MapPin } from "lucide-react";
import Link from "next/link";

import { CeapLogo } from "@/components/brand/ceap-logo";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import { cn } from "@/lib/utils";

const FOOTER_SECTIONS: { title: string; links: { href: string; label: string }[] }[] = [
  {
    title: "Produto",
    links: [
      { href: "/#jornada", label: "Como funciona" },
      { href: "/#cursos", label: "Cursos" },
      { href: "/#ingresso", label: "Processo seletivo" },
    ],
  },
  {
    title: "Conta",
    links: [
      { href: "/cadastro", label: "Criar conta" },
      { href: "/login", label: "Entrar" },
    ],
  },
];

/**
 * Rodapé institucional, reutilizado na Landing Page e nas páginas públicas
 * (cadastro/login). Usa âncoras absolutas (`/#secao`) para funcionar a partir
 * de qualquer rota.
 */
export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border/60 bg-background">
      <div
        className={cn(
          LANDING_CONTAINER_CLASS,
          "grid gap-10 py-14 sm:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr]",
        )}
      >
        <div className="flex flex-col gap-4">
          <CeapLogo />
          <p className="text-sm font-medium text-brand italic">
            Educação além da educação
          </p>
          <p className="max-w-xs text-sm text-muted-foreground">
            A experiência do candidato do processo seletivo do CEAP — Centro Educacional
            Assistencial Profissionalizante.
          </p>
          <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin className="size-4 text-brand" aria-hidden="true" />
            Pedreira · São Paulo — SP
          </p>
        </div>

        {FOOTER_SECTIONS.map((section) => (
          <nav
            key={section.title}
            aria-label={section.title}
            className="flex flex-col gap-3"
          >
            <span className="text-sm font-semibold text-foreground">{section.title}</span>
            {section.links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        ))}
      </div>

      <div className="border-t border-border/60">
        <div
          className={cn(
            LANDING_CONTAINER_CLASS,
            "flex flex-col gap-2 py-6 sm:flex-row sm:items-center sm:justify-between",
          )}
        >
          <p className="text-xs text-muted-foreground">
            © {year} CEAP Connect. Todos os direitos reservados.
          </p>
          <p className="text-xs text-muted-foreground">
            Plataforma de Candidate Experience · CEAP — Centro Educacional Assistencial
            Profissionalizante
          </p>
        </div>
      </div>
    </footer>
  );
}
