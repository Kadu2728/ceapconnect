import { Card } from "@/components/ui/card";
import type { DailyCount } from "@/features/admin/types/admin.types";

const MAX_BAR_PX = 140;

function formatDay(iso: string): string {
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit" }).format(
    new Date(`${iso}T00:00:00`),
  );
}

interface SignupsChartProps {
  data: DailyCount[];
}

/**
 * Gráfico de barras (cadastros por dia) — SVG/CSS puro, sem biblioteca de
 * charts, para não pesar o bundle. Barra mais alta = dia com mais cadastros.
 */
export function SignupsChart({ data }: SignupsChartProps) {
  const max = Math.max(1, ...data.map((point) => point.count));

  return (
    <Card className="h-full gap-4">
      <div className="px-6">
        <h3 className="font-semibold">Cadastros por dia</h3>
        <p className="text-sm text-muted-foreground">Novos alunos nos últimos 14 dias</p>
      </div>

      <div className="px-6 pb-2">
        {data.length === 0 ? (
          <p className="py-12 text-center text-sm text-muted-foreground">
            Nenhum cadastro no período.
          </p>
        ) : (
          <div className="flex items-end justify-between gap-1.5">
            {data.map((point) => {
              const height =
                point.count > 0
                  ? Math.max(6, Math.round((point.count / max) * MAX_BAR_PX))
                  : 2;
              return (
                <div
                  key={point.date}
                  className="flex flex-1 flex-col items-center gap-1.5"
                  title={`${point.count} cadastro(s) em ${formatDay(point.date)}`}
                >
                  <span className="text-xs font-medium tabular-nums text-muted-foreground">
                    {point.count > 0 ? point.count : ""}
                  </span>
                  <div
                    className="w-full max-w-[2rem] rounded-t bg-gradient-to-t from-brand to-brand-2"
                    style={{ height }}
                  />
                  <span className="text-[10px] text-muted-foreground">
                    {formatDay(point.date)}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Card>
  );
}
