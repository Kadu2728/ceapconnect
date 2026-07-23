import { Layers } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { LevelBucket } from "@/features/admin/types/admin.types";

interface LevelDistributionChartProps {
  data: LevelBucket[];
}

/**
 * Distribuição de alunos por nível — barras horizontais (CSS puro, sem lib de
 * charts). Mostra de relance onde a base está concentrada e como a progressão
 * se espalha, reforçando o efeito da gamificação para a gestão.
 */
export function LevelDistributionChart({ data }: LevelDistributionChartProps) {
  const max = Math.max(1, ...data.map((bucket) => bucket.count));
  const totalStudents = data.reduce((sum, bucket) => sum + bucket.count, 0);

  return (
    <Card className="h-full gap-4">
      <div className="flex items-center gap-2 px-6">
        <Layers className="size-5 text-brand" aria-hidden="true" />
        <div>
          <h3 className="font-semibold">Distribuição por nível</h3>
          <p className="text-sm text-muted-foreground">Onde os alunos estão na jornada</p>
        </div>
      </div>

      <ul className="flex flex-col gap-3 px-6 pb-2">
        {data.map((bucket) => {
          const width = totalStudents > 0 ? Math.round((bucket.count / max) * 100) : 0;
          const share =
            totalStudents > 0 ? Math.round((bucket.count / totalStudents) * 100) : 0;
          return (
            <li key={bucket.level} className="flex items-center gap-3">
              <span className="w-28 shrink-0 truncate text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Nv.{bucket.level}</span>{" "}
                {bucket.name}
              </span>
              <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-brand to-brand-green transition-[width] duration-700"
                  style={{ width: `${width}%` }}
                />
              </div>
              <span className="w-16 shrink-0 text-right text-sm tabular-nums">
                <span className="font-semibold">{bucket.count}</span>
                <span className="ml-1 text-xs text-muted-foreground">{share}%</span>
              </span>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}
