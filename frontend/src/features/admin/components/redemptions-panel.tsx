"use client";

import { Check, Clock, Gift } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useFulfillRedemption } from "@/features/admin/hooks/use-fulfill-redemption";
import type {
  AdminRedemption,
  AdminRedemptionList,
} from "@/features/admin/types/admin.types";

interface RedemptionsPanelProps {
  data: AdminRedemptionList;
}

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

/**
 * Fila de resgates de recompensas para a equipe do CEAP: quem resgatou o quê e
 * quando, com a ação de confirmar a entrega. Fecha o ciclo operacional da
 * gamificação — o resgate do aluno vira uma tarefa real e rastreável para o time.
 */
export function RedemptionsPanel({ data }: RedemptionsPanelProps) {
  return (
    <Card className="gap-4">
      <div className="flex items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <Gift className="size-5 text-brand" aria-hidden="true" />
          <h2 className="font-semibold">Resgates de recompensas</h2>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-orange/15 px-3 py-1 text-sm font-semibold text-brand-orange">
          <Clock className="size-4" aria-hidden="true" />
          {data.pending_count} pendente(s)
        </span>
      </div>

      {data.redemptions.length === 0 ? (
        <p className="px-6 text-sm text-muted-foreground">
          Nenhum resgate ainda. Assim que um aluno resgatar uma recompensa, ela aparece
          aqui para você confirmar a entrega.
        </p>
      ) : (
        <ul className="divide-y divide-border/60">
          {data.redemptions.map((redemption) => (
            <RedemptionRow key={redemption.id} redemption={redemption} />
          ))}
        </ul>
      )}
    </Card>
  );
}

function RedemptionRow({ redemption }: { redemption: AdminRedemption }) {
  const fulfillMutation = useFulfillRedemption();
  const isPending = redemption.status === "pending";

  return (
    <li className="flex flex-col gap-3 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <p className="truncate font-medium">{redemption.reward_title}</p>
        <p className="truncate text-sm text-muted-foreground">
          {redemption.student_name} · {redemption.student_email}
        </p>
        <p className="mt-0.5 text-xs text-muted-foreground">
          Resgatada em {formatDate(redemption.redeemed_at)}
        </p>
      </div>

      <div className="shrink-0">
        {isPending ? (
          <Button
            size="sm"
            onClick={() => fulfillMutation.mutate(redemption.id)}
            disabled={fulfillMutation.isPending}
          >
            {fulfillMutation.isPending ? "Confirmando…" : "Confirmar entrega"}
          </Button>
        ) : (
          <span className="inline-flex items-center gap-1.5 text-sm font-medium text-success">
            <Check className="size-4" aria-hidden="true" />
            Entregue
            {redemption.fulfilled_at ? ` · ${formatDate(redemption.fulfilled_at)}` : null}
          </span>
        )}
      </div>
    </li>
  );
}
