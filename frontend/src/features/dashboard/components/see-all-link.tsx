import { ArrowRight } from "lucide-react";
import Link from "next/link";

interface SeeAllLinkProps {
  href: string;
  /** Rótulo visível ("Ver todas"); o `aria-label` diz *o quê* ("Ver todas as conquistas"). */
  label: string;
  ariaLabel: string;
}

/**
 * Link discreto no cabeçalho de um card do Dashboard para a página completa
 * da seção. Existe porque a bottom navigation mobile mostra só 5 destinos:
 * Conquistas e Eventos precisam continuar a um toque a partir da home.
 */
export function SeeAllLink({ href, label, ariaLabel }: SeeAllLinkProps) {
  return (
    <Link
      href={href}
      aria-label={ariaLabel}
      className="touch-target inline-flex shrink-0 items-center gap-1 text-sm font-medium text-brand hover:underline"
    >
      {label}
      <ArrowRight className="size-3.5" aria-hidden="true" />
    </Link>
  );
}
