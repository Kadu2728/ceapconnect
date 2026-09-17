"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FIELD_CLASS } from "@/features/admin/components/learning/course-form";
import { useSaveModule } from "@/features/admin/hooks/use-admin-learning";
import type {
  AdminModule,
  AdminModuleInput,
} from "@/features/admin/types/admin-learning.types";

interface ModuleFormProps {
  courseId: string;
  module?: AdminModule;
  /** Sugestão para um módulo novo: próximo número livre. */
  suggestedOrder: number;
  onClose: () => void;
}

/** Formulário inline de módulo. Reordenar = editar o número da ordem. */
export function ModuleForm({
  courseId,
  module,
  suggestedOrder,
  onClose,
}: ModuleFormProps) {
  const [input, setInput] = useState<AdminModuleInput>({
    title: module?.title ?? "",
    description: module?.description ?? null,
    order: module?.order ?? suggestedOrder,
  });
  const save = useSaveModule(courseId);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    save.mutate(
      { id: module?.id, input: { ...input, description: input.description || null } },
      { onSuccess: onClose },
    );
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-xl border bg-muted/30 p-4"
    >
      <div className="grid gap-3 sm:grid-cols-[1fr_6rem]">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`module-title-${module?.id ?? "new"}`}>Título do módulo</Label>
          <Input
            id={`module-title-${module?.id ?? "new"}`}
            value={input.title}
            onChange={(e) => setInput({ ...input, title: e.target.value })}
            required
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`module-order-${module?.id ?? "new"}`}>Ordem</Label>
          <Input
            id={`module-order-${module?.id ?? "new"}`}
            type="number"
            min={1}
            value={input.order}
            onChange={(e) => setInput({ ...input, order: Number(e.target.value) })}
            required
          />
        </div>
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor={`module-desc-${module?.id ?? "new"}`}>Descrição (opcional)</Label>
        <textarea
          id={`module-desc-${module?.id ?? "new"}`}
          className={`${FIELD_CLASS} min-h-16`}
          value={input.description ?? ""}
          onChange={(e) => setInput({ ...input, description: e.target.value })}
        />
      </div>
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={save.isPending}>
          {save.isPending ? "Salvando…" : module ? "Salvar" : "Criar módulo"}
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={onClose}>
          Cancelar
        </Button>
      </div>
    </form>
  );
}
