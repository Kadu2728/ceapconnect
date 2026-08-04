"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSaveReward } from "@/features/admin/hooks/use-save-reward";
import type {
  AdminAchievementOption,
  AdminReward,
  AdminRewardInput,
  RewardUnlockType,
} from "@/features/admin/types/admin.types";
import { cn } from "@/lib/utils";

/** Faixas de nível (espelham `app/core/gamification.py::LEVEL_TIERS`). */
const LEVEL_OPTIONS = [
  { value: 1, label: "Nível 1 · Iniciante" },
  { value: 2, label: "Nível 2 · Explorador" },
  { value: 3, label: "Nível 3 · Construtor" },
  { value: 4, label: "Nível 4 · Estrategista" },
  { value: 5, label: "Nível 5 · Especialista" },
  { value: 6, label: "Nível 6 · Mestre CEAP" },
];

/** Ícones suportados (ver `features/rewards/utils/reward-icons.ts`). */
const ICON_HINT =
  "cloud, monitor, laptop, clapperboard, network, table, languages, badge-check, graduation-cap, code, palette, sparkles, award";

const FIELD_CLASS =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50";

function buildInitialInput(reward?: AdminReward): AdminRewardInput {
  return {
    title: reward?.title ?? "",
    description: reward?.description ?? "",
    provider: reward?.provider ?? "",
    category: reward?.category ?? "Curso",
    icon: reward?.icon ?? "graduation-cap",
    unlock_type: reward?.unlock_type ?? "level",
    required_level: reward?.required_level ?? 1,
    required_achievement_id: reward?.required_achievement_id ?? null,
    featured: reward?.featured ?? false,
    is_active: reward?.is_active ?? true,
    sort_order: reward?.sort_order ?? 0,
  };
}

interface RewardFormProps {
  reward?: AdminReward;
  achievements: AdminAchievementOption[];
  onClose: () => void;
}

/**
 * Formulário inline de criação/edição de recompensa. A condição de desbloqueio
 * alterna entre "por nível" e "por conquista", mostrando só o seletor pertinente
 * — espelha a validação do backend e evita estados inconsistentes.
 */
export function RewardForm({ reward, achievements, onClose }: RewardFormProps) {
  const [input, setInput] = useState<AdminRewardInput>(() => buildInitialInput(reward));
  const saveReward = useSaveReward();

  const isEditing = Boolean(reward);

  function set<K extends keyof AdminRewardInput>(key: K, value: AdminRewardInput[K]) {
    setInput((prev) => ({ ...prev, [key]: value }));
  }

  function setUnlockType(type: RewardUnlockType) {
    setInput((prev) => ({
      ...prev,
      unlock_type: type,
      required_level: type === "level" ? (prev.required_level ?? 1) : null,
      required_achievement_id:
        type === "achievement"
          ? (prev.required_achievement_id ?? achievements[0]?.id ?? null)
          : null,
    }));
  }

  const requirementValid =
    input.unlock_type === "level"
      ? input.required_level !== null
      : Boolean(input.required_achievement_id);
  const canSave =
    input.title.trim().length >= 2 &&
    input.description.trim().length >= 2 &&
    input.provider.trim().length >= 1 &&
    requirementValid &&
    !saveReward.isPending;

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSave) return;
    saveReward.mutate({ id: reward?.id, input }, { onSuccess: () => onClose() });
  }

  return (
    <Card className="gap-5 border-brand/30">
      <div className="px-6">
        <h3 className="font-semibold">
          {isEditing ? "Editar recompensa" : "Nova recompensa"}
        </h3>
        <p className="text-sm text-muted-foreground">
          Preencha os dados. Mudanças refletem na vitrine dos alunos imediatamente.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4 px-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-1.5 sm:col-span-2">
            <Label htmlFor="rw-title">Título</Label>
            <Input
              id="rw-title"
              value={input.title}
              onChange={(e) => set("title", e.target.value)}
              maxLength={200}
              placeholder="AWS Cloud Practitioner"
            />
          </div>

          <div className="flex flex-col gap-1.5 sm:col-span-2">
            <Label htmlFor="rw-desc">Descrição</Label>
            <textarea
              id="rw-desc"
              value={input.description}
              onChange={(e) => set("description", e.target.value)}
              maxLength={2000}
              rows={3}
              className={cn(FIELD_CLASS, "h-auto resize-y")}
              placeholder="O que o aluno ganha e por que vale a pena."
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="rw-provider">Instituição</Label>
            <Input
              id="rw-provider"
              value={input.provider}
              onChange={(e) => set("provider", e.target.value)}
              maxLength={120}
              placeholder="Amazon Web Services"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="rw-category">Categoria</Label>
            <Input
              id="rw-category"
              value={input.category}
              onChange={(e) => set("category", e.target.value)}
              maxLength={60}
              placeholder="Certificação"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="rw-icon">Ícone</Label>
            <Input
              id="rw-icon"
              value={input.icon}
              onChange={(e) => set("icon", e.target.value)}
              maxLength={50}
              placeholder="cloud"
            />
            <span className="text-xs text-muted-foreground">Opções: {ICON_HINT}</span>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="rw-sort">Ordem de exibição</Label>
            <Input
              id="rw-sort"
              type="number"
              min={0}
              value={input.sort_order}
              onChange={(e) => set("sort_order", Number(e.target.value) || 0)}
            />
          </div>
        </div>

        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-sm font-medium">Como desbloqueia</legend>
          <div className="flex gap-2">
            <UnlockTypeButton
              active={input.unlock_type === "level"}
              label="Por nível"
              onClick={() => setUnlockType("level")}
            />
            <UnlockTypeButton
              active={input.unlock_type === "achievement"}
              label="Por conquista"
              onClick={() => setUnlockType("achievement")}
            />
          </div>

          {input.unlock_type === "level" ? (
            <select
              aria-label="Nível necessário"
              className={cn(FIELD_CLASS, "mt-1")}
              value={input.required_level ?? 1}
              onChange={(e) => set("required_level", Number(e.target.value))}
            >
              {LEVEL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          ) : (
            <select
              aria-label="Conquista necessária"
              className={cn(FIELD_CLASS, "mt-1")}
              value={input.required_achievement_id ?? ""}
              onChange={(e) => set("required_achievement_id", e.target.value || null)}
            >
              <option value="" disabled>
                Selecione uma conquista
              </option>
              {achievements.map((achievement) => (
                <option key={achievement.id} value={achievement.id}>
                  {achievement.name}
                </option>
              ))}
            </select>
          )}
        </fieldset>

        <div className="flex flex-wrap gap-6">
          <label className="flex cursor-pointer items-center gap-2 text-sm">
            <Checkbox
              checked={input.featured}
              onChange={(e) => set("featured", e.target.checked)}
            />
            Destaque na vitrine
          </label>
          <label className="flex cursor-pointer items-center gap-2 text-sm">
            <Checkbox
              checked={input.is_active}
              onChange={(e) => set("is_active", e.target.checked)}
            />
            Ativa (visível para os alunos)
          </label>
        </div>

        <div className="flex gap-3">
          <Button type="submit" disabled={!canSave}>
            {saveReward.isPending
              ? "Salvando…"
              : isEditing
                ? "Salvar alterações"
                : "Criar recompensa"}
          </Button>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancelar
          </Button>
        </div>
      </form>
    </Card>
  );
}

function UnlockTypeButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "rounded-md border px-3 py-1.5 text-sm font-medium transition-colors",
        active
          ? "border-brand bg-brand/10 text-brand"
          : "border-input text-muted-foreground hover:bg-accent/50",
      )}
    >
      {label}
    </button>
  );
}
