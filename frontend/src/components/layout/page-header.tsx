interface PageHeaderProps {
  title: string;
  description?: string;
}

/**
 * Cabeçalho padrão das páginas autenticadas (Missões, Conquistas, Eventos),
 * garantindo ritmo tipográfico consistente entre elas.
 */
export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-8 flex flex-col gap-1.5">
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{title}</h1>
      {description ? (
        <p className="text-pretty text-muted-foreground">{description}</p>
      ) : null}
    </div>
  );
}
