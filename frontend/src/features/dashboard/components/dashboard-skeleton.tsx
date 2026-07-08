/**
 * Esqueleto do Dashboard (EPIC 03), exibido enquanto a store de autenticação
 * reidrata do `localStorage` (evitando redirecionamento precoce) e enquanto
 * `GET /api/v1/dashboard` está em andamento.
 *
 * O silhouette reproduz o formato real do layout final (saudação + XP,
 * contagem da prova, jornada + missão, eventos, conquistas) em vez de um
 * spinner genérico — skeletons que espelham a estrutura da tela final
 * transmitem mais velocidade percebida (UI_UX_GUIDELINES.md).
 */
export function DashboardSkeleton() {
  return (
    <div aria-hidden="true" className="flex animate-pulse flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-col gap-2">
          <div className="h-4 w-24 rounded-md bg-muted" />
          <div className="h-8 w-48 rounded-md bg-muted" />
        </div>
        <div className="h-9 w-28 rounded-full bg-muted" />
      </div>

      <div className="h-20 rounded-2xl border bg-card" />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="flex flex-col gap-6 lg:col-span-2">
          <div className="h-56 rounded-2xl border bg-card" />
          <div className="h-44 rounded-2xl border bg-card" />
        </div>
        <div className="h-64 rounded-2xl border bg-card" />
      </div>

      <div className="h-40 rounded-2xl border bg-card" />
    </div>
  );
}
