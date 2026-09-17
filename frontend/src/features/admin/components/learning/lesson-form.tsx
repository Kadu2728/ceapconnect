"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FIELD_CLASS } from "@/features/admin/components/learning/course-form";
import { useSaveLesson } from "@/features/admin/hooks/use-admin-learning";
import type {
  AdminLesson,
  AdminLessonInput,
} from "@/features/admin/types/admin-learning.types";
import type { VideoProvider } from "@/features/learning/types/learning.types";

interface LessonFormProps {
  courseId: string;
  moduleId: string;
  lesson?: AdminLesson;
  suggestedOrder: number;
  providers: VideoProvider[];
  completionThreshold: number;
  onClose: () => void;
}

/** Formulário inline de aula — o único lugar onde a URL do vídeo é editada. */
export function LessonForm({
  courseId,
  moduleId,
  lesson,
  suggestedOrder,
  providers,
  completionThreshold,
  onClose,
}: LessonFormProps) {
  const uid = lesson?.id ?? `new-${moduleId}`;
  const [input, setInput] = useState<AdminLessonInput>({
    title: lesson?.title ?? "",
    description: lesson?.description ?? null,
    video_provider: lesson?.video_provider ?? "url",
    video_ref: lesson?.video_ref ?? "",
    duration_seconds: lesson?.duration_seconds ?? 60,
    order: lesson?.order ?? suggestedOrder,
    is_active: lesson?.is_active ?? true,
  });
  const save = useSaveLesson(courseId);

  const set = <K extends keyof AdminLessonInput>(key: K, value: AdminLessonInput[K]) =>
    setInput((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    save.mutate(
      {
        id: lesson?.id,
        moduleId,
        input: { ...input, description: input.description || null },
      },
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
          <Label htmlFor={`lesson-title-${uid}`}>Título da aula</Label>
          <Input
            id={`lesson-title-${uid}`}
            value={input.title}
            onChange={(e) => set("title", e.target.value)}
            required
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`lesson-order-${uid}`}>Ordem</Label>
          <Input
            id={`lesson-order-${uid}`}
            type="number"
            min={1}
            value={input.order}
            onChange={(e) => set("order", Number(e.target.value))}
            required
          />
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor={`lesson-desc-${uid}`}>Descrição (opcional)</Label>
        <textarea
          id={`lesson-desc-${uid}`}
          className={`${FIELD_CLASS} min-h-16`}
          value={input.description ?? ""}
          onChange={(e) => set("description", e.target.value)}
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-[8rem_1fr_7rem]">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`lesson-provider-${uid}`}>Origem</Label>
          <select
            id={`lesson-provider-${uid}`}
            className={FIELD_CLASS}
            value={input.video_provider}
            onChange={(e) => set("video_provider", e.target.value as VideoProvider)}
          >
            {providers.map((p) => (
              <option key={p} value={p}>
                {p === "url" ? "URL direta" : p}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`lesson-ref-${uid}`}>URL do vídeo (.mp4)</Label>
          <Input
            id={`lesson-ref-${uid}`}
            value={input.video_ref}
            onChange={(e) => set("video_ref", e.target.value)}
            placeholder="https://…/aula-01.mp4"
            required
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor={`lesson-duration-${uid}`}>Duração (s)</Label>
          <Input
            id={`lesson-duration-${uid}`}
            type="number"
            min={1}
            value={input.duration_seconds}
            onChange={(e) => set("duration_seconds", Number(e.target.value))}
            required
          />
        </div>
      </div>
      <p className="text-xs text-muted-foreground">
        A duração precisa ser a real do arquivo: a aula conta como concluída aos{" "}
        {Math.round(completionThreshold * 100)}% assistidos. Um valor maior que o vídeo
        deixa a aula eternamente &ldquo;em andamento&rdquo;.
      </p>

      <label className="flex items-center gap-2 text-sm">
        <Checkbox
          checked={input.is_active}
          onChange={(e) => set("is_active", e.target.checked)}
        />
        Aula ativa (visível para o público)
      </label>

      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={save.isPending}>
          {save.isPending ? "Salvando…" : lesson ? "Salvar" : "Criar aula"}
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={onClose}>
          Cancelar
        </Button>
      </div>
    </form>
  );
}
