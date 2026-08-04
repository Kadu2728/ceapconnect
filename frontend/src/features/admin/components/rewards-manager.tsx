"use client";

import { Lock, Plus, Settings2, Star } from "lucide-react";
import { createElement, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { RewardForm } from "@/features/admin/components/reward-form";
import type { AdminReward, AdminRewardList } from "@/features/admin/types/admin.types";
import { resolveRewardIcon } from "@/features/rewards/utils/reward-icons";
import { cn } from "@/lib/utils";

interface RewardsManagerProps {
  data: AdminRewardList;
}

/** Estado de edição: `null` fechado, `"new"` criando, ou a recompensa em edição. */
type EditingState = AdminReward | "new" | null;

/**
 * Gestão do catálogo de recompensas: cria, edita e ativa/desativa cursos e
 * prêmios direto no painel — sem depender de seed/DB. Dá autonomia ao CEAP para
 * curar as recompensas reais oferecidas aos alunos.
 */
export function RewardsManager({ data }: RewardsManagerProps) {
  const [editing, setEditing] = useState<EditingState>(null);

  return (
    <Card className="gap-4">
      <div className="flex items-center justify-between gap-3 px-6">
        <div className="flex items-center gap-2">
          <Settings2 className="size-5 text-brand" aria-hidden="true" />
          <div>
            <h2 className="font-semibold">Gerenciar recompensas</h2>
            <p className="text-sm text-muted-foreground">
              {data.rewards.length} no catálogo ·{" "}
              {data.rewards.filter((r) => r.is_active).length} ativa(s)
            </p>
          </div>
        </div>
        {editing === null ? (
          <Button size="sm" onClick={() => setEditing("new")}>
            <Plus className="size-4" aria-hidden="true" />
            Nova recompensa
          </Button>
        ) : null}
      </div>

      {editing !== null ? (
        <div className="px-6">
          <RewardForm
            reward={editing === "new" ? undefined : editing}
            achievements={data.achievements}
            onClose={() => setEditing(null)}
          />
        </div>
      ) : null}

      <ul className="divide-y divide-border/60">
        {data.rewards.map((reward) => (
          <RewardRow
            key={reward.id}
            reward={reward}
            onEdit={() => setEditing(reward)}
            disabled={editing !== null}
          />
        ))}
      </ul>
    </Card>
  );
}

function RewardRow({
  reward,
  onEdit,
  disabled,
}: {
  reward: AdminReward;
  onEdit: () => void;
  disabled: boolean;
}) {
  const requirement =
    reward.unlock_type === "level"
      ? `Nível ${reward.required_level}`
      : `Conquista: ${reward.required_achievement_name ?? "—"}`;

  return (
    <li
      className={cn(
        "flex items-center gap-3 px-6 py-3.5",
        !reward.is_active && "opacity-60",
      )}
    >
      <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand/15 to-brand-green/15 text-brand">
        {createElement(resolveRewardIcon(reward.icon), {
          className: "size-5",
          "aria-hidden": true,
        })}
      </span>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <p className="truncate text-sm font-medium">{reward.title}</p>
          {reward.featured ? (
            <Star className="size-3.5 shrink-0 text-brand-orange" aria-hidden="true" />
          ) : null}
          {!reward.is_active ? (
            <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
              <Lock className="size-3" aria-hidden="true" />
              Inativa
            </span>
          ) : null}
        </div>
        <p className="truncate text-xs text-muted-foreground">
          {reward.provider} · {requirement}
        </p>
      </div>

      <Button size="sm" variant="outline" onClick={onEdit} disabled={disabled}>
        Editar
      </Button>
    </li>
  );
}
