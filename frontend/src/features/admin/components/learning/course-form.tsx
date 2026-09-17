"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSaveCourse } from "@/features/admin/hooks/use-admin-learning";
import type {
  AdminCourse,
  AdminCourseInput,
} from "@/features/admin/types/admin-learning.types";
import type { CourseAudience } from "@/features/learning/types/learning.types";

export const FIELD_CLASS =
  "flex w-full rounded-md border border-input bg-transparent px-3 py-1.5 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50";

const AUDIENCE_LABEL: Record<CourseAudience, string> = {
  guardian: "Responsáveis · Formação de Pais",
  candidate: "Alunos · Preparação",
};

function buildInput(course?: AdminCourse): AdminCourseInput {
  return {
    slug: course?.slug ?? "",
    title: course?.title ?? "",
    description: course?.description ?? "",
    audience: course?.audience ?? "guardian",
    thumbnail_url: course?.thumbnail_url ?? null,
    is_active: course?.is_active ?? true,
  };
}

interface CourseFormProps {
  course?: AdminCourse;
  audiences: CourseAudience[];
  onClose: () => void;
}

/** Formulário inline de curso — mesmo desenho de `RewardForm`. */
export function CourseForm({ course, audiences, onClose }: CourseFormProps) {
  const [input, setInput] = useState<AdminCourseInput>(() => buildInput(course));
  const save = useSaveCourse();

  const set = <K extends keyof AdminCourseInput>(key: K, value: AdminCourseInput[K]) =>
    setInput((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    save.mutate(
      { id: course?.id, input: { ...input, thumbnail_url: input.thumbnail_url || null } },
      { onSuccess: onClose },
    );
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 rounded-xl border bg-muted/30 p-4"
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="course-title">Título</Label>
          <Input
            id="course-title"
            value={input.title}
            onChange={(e) => set("title", e.target.value)}
            required
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="course-slug">Slug (URL)</Label>
          <Input
            id="course-slug"
            value={input.slug}
            onChange={(e) => set("slug", e.target.value)}
            placeholder="formacao-de-pais"
            required
            disabled={Boolean(course)}
          />
          {course ? (
            <p className="text-xs text-muted-foreground">
              O slug não muda depois de publicado.
            </p>
          ) : null}
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="course-description">Descrição</Label>
        <textarea
          id="course-description"
          className={`${FIELD_CLASS} min-h-20`}
          value={input.description}
          onChange={(e) => set("description", e.target.value)}
          required
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="course-audience">Público</Label>
          <select
            id="course-audience"
            className={FIELD_CLASS}
            value={input.audience}
            onChange={(e) => set("audience", e.target.value as CourseAudience)}
          >
            {audiences.map((audience) => (
              <option key={audience} value={audience}>
                {AUDIENCE_LABEL[audience]}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="course-thumb">Thumbnail (URL, opcional)</Label>
          <Input
            id="course-thumb"
            value={input.thumbnail_url ?? ""}
            onChange={(e) => set("thumbnail_url", e.target.value)}
            placeholder="https://…/capa.webp"
          />
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm">
        <Checkbox
          checked={input.is_active}
          onChange={(e) => set("is_active", e.target.checked)}
        />
        Curso ativo (visível para o público)
      </label>

      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={save.isPending}>
          {save.isPending ? "Salvando…" : course ? "Salvar alterações" : "Criar curso"}
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={onClose}>
          Cancelar
        </Button>
      </div>
    </form>
  );
}
