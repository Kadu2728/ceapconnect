import { Activity, Clock, TrendingDown, TrendingUp, type LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { InterventionImpact } from "@/features/admin/types/admin.types";
import { cn } from "@/lib/utils";

interface InterventionImpactCardProps {
  data: InterventionImpact;
}

/**
 * Fecha o loop do Console de Risco (EPIC 14): "os coordenadores contataram
 * candidatos em risco — funcionou?" Mostra o resultado medido 7 dias após
 * cada intervenção (o risco caiu? o candidato voltou a ter atividade?).
 *
 * Estado vazio deliberado: com poucas ou nenhuma intervenção medida, mostra
 * uma mensagem de contexto em vez de "0%" — um zero aqui seria enganoso
 * (parece "não funcionou" quando na verdade é "ainda não deu tempo de medir").
 */
export function InterventionImpactCard({ data }: InterventionImpactCardProps) {
  const hasMeasuredData = data.measured > 0;
  const riskFell = data.avg_score_delta !== null && data.avg_score_delta < 0;
  const riskRose = data.avg_score_delta !== null && data.avg_score_delta > 0;

  return (
    <Card className="gap-4">
      <div className="flex items-center gap-2 px-6">
        <Activity className="size-5 text-brand" aria-hidden="true" />
        <div>
          <h3 className="font-semibold">Impacto das intervenções</h3>
          <p className="text-sm text-muted-foreground">
            Últimos 30 dias · Console de Risco
          </p>
        </div>
      </div>

      {!hasMeasuredData ? (
        <div className="flex items-start gap-3 px-6 pb-2">
          <Clock
            className="mt-0.5 size-5 shrink-0 text-muted-foreground"
            aria-hidden="true"
          />
          <p className="text-sm text-muted-foreground">
            {data.total > 0
              ? `${data.total} intervenção(ões) registrada(s) — o resultado é medido automaticamente 7 dias após o contato.`
              : "Nenhuma intervenção registrada ainda. Os resultados aparecem aqui assim que os coordenadores contatarem candidatos em risco."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 px-6 pb-2 sm:grid-cols-3">
          <ImpactStat
            label="Risco médio"
            value={
              data.avg_score_delta === null
                ? "—"
                : `${data.avg_score_delta > 0 ? "+" : ""}${data.avg_score_delta} pts`
            }
            hint={
              riskFell
                ? "caiu após o contato"
                : riskRose
                  ? "subiu após o contato"
                  : "sem mudança"
            }
            icon={riskRose ? TrendingUp : TrendingDown}
            tone={
              riskFell
                ? "text-success"
                : riskRose
                  ? "text-destructive"
                  : "text-muted-foreground"
            }
          />
          <ImpactStat
            label="Melhoraram"
            value={data.pct_improved !== null ? `${data.pct_improved}%` : "—"}
            hint={`de ${data.measured} medida(s)`}
          />
          <ImpactStat
            label="Voltaram a interagir"
            value={
              data.pct_had_activity_after !== null
                ? `${data.pct_had_activity_after}%`
                : "—"
            }
            hint="tiveram atividade após o contato"
          />
        </div>
      )}

      {data.pending_measurement > 0 ? (
        <p className="px-6 text-xs text-muted-foreground">
          {data.pending_measurement} intervenção(ões) ainda aguardando os 7 dias para
          medir o resultado.
        </p>
      ) : null}
    </Card>
  );
}

interface ImpactStatProps {
  label: string;
  value: string;
  hint: string;
  icon?: LucideIcon;
  tone?: string;
}

function ImpactStat({ label, value, hint, icon: Icon, tone }: ImpactStatProps) {
  return (
    <div>
      <p className="text-sm text-muted-foreground">{label}</p>
      <p
        className={cn(
          "mt-1 flex items-center gap-1.5 text-2xl font-bold tabular-nums",
          tone,
        )}
      >
        {Icon ? <Icon className="size-5 shrink-0" aria-hidden="true" /> : null}
        {value}
      </p>
      <p className="mt-0.5 text-xs text-muted-foreground">{hint}</p>
    </div>
  );
}
