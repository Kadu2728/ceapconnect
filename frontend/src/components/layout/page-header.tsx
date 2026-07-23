interface PageHeaderProps {
  title: string;
  description?: string;
  /** Rótulo curto acima do título (ex.: "Sua jornada"), opcional. */
  eyebrow?: string;
}

/**
 * Cabeçalho padrão das páginas autenticadas (Missões, Conquistas, Eventos…),
 * garantindo ritmo tipográfico consistente. O acento vertical em gradiente de
 * marca dá identidade e ancora o título visualmente sem poluir.
 */
export function PageHeader({ title, description, eyebrow }: PageHeaderProps) {
  return (
    <div className="mb-8 flex items-stretch gap-3">
      <span
        aria-hidden="true"
        className="w-1 shrink-0 rounded-full bg-gradient-to-b from-brand to-brand-green"
      />
      <div className="flex flex-col gap-1.5">
        {eyebrow ? (
          <span className="text-xs font-semibold uppercase tracking-wider text-brand">
            {eyebrow}
          </span>
        ) : null}
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{title}</h1>
        {description ? (
          <p className="max-w-2xl text-pretty text-muted-foreground">{description}</p>
        ) : null}
      </div>
    </div>
  );
}
