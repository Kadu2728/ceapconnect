interface CardListSkeletonProps {
  count?: number;
  withSummary?: boolean;
}

/**
 * Placeholder de carregamento para listas em card (Missões, Eventos). Reserva
 * o espaço do conteúdo real para evitar layout shift (CLS) enquanto a query
 * resolve.
 */
export function CardListSkeleton({
  count = 4,
  withSummary = false,
}: CardListSkeletonProps) {
  return (
    <div className="flex flex-col gap-6">
      {withSummary ? (
        <div className="h-28 animate-pulse rounded-xl border border-border/60 bg-card" />
      ) : null}

      <div className="flex flex-col gap-4">
        {Array.from({ length: count }).map((_, index) => (
          <div
            key={index}
            className="h-32 animate-pulse rounded-xl border border-border/60 bg-card"
          />
        ))}
      </div>
    </div>
  );
}
