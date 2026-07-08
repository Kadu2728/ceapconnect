import { cn } from "@/lib/utils";

interface CeapMarkProps {
  className?: string;
}

/**
 * Marca gráfica do CEAP Connect.
 *
 * Reinterpreta a identidade do CEAP — Centro Educacional Assistencial
 * Profissionalizante: o cluster de círculos coloridos do logo (azul, verde,
 * roxo e laranja), símbolo de diversidade e comunidade de jovens. Puro SVG,
 * escalável e theme-aware (cores vêm dos tokens de marca via `fill-*`).
 */
export function CeapMark({ className }: CeapMarkProps) {
  return (
    <svg
      viewBox="0 0 40 40"
      fill="none"
      className={cn("size-8", className)}
      aria-hidden="true"
    >
      <circle cx="14" cy="14.5" r="6.6" className="fill-brand-2" />
      <circle cx="26" cy="15" r="8.2" className="fill-brand-green" />
      <circle cx="15" cy="27" r="7.2" className="fill-brand-purple" />
      <circle cx="26.5" cy="28.5" r="5" className="fill-brand-orange" />
    </svg>
  );
}

interface CeapLogoProps {
  className?: string;
  markClassName?: string;
  /** Oculta o texto, mantendo só a marca gráfica (ex.: espaços estreitos). */
  hideWordmark?: boolean;
  /**
   * Classes extras no wordmark — útil para ocultá-lo de forma responsiva em
   * telas muito estreitas (ex.: `hidden min-[360px]:inline` na Navbar).
   */
  wordmarkClassName?: string;
}

/**
 * Lockup completo do CEAP Connect: marca gráfica + wordmark.
 *
 * Usado na Navbar, no Footer e nas telas públicas (cadastro/login) para
 * manter a assinatura visual consistente em todo o fluxo do candidato.
 */
export function CeapLogo({
  className,
  markClassName,
  hideWordmark = false,
  wordmarkClassName,
}: CeapLogoProps) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <CeapMark className={markClassName} />
      {!hideWordmark ? (
        <span
          className={cn(
            "text-lg font-bold tracking-tight text-foreground",
            wordmarkClassName,
          )}
        >
          CEAP<span className="text-brand"> Connect</span>
        </span>
      ) : null}
    </span>
  );
}
