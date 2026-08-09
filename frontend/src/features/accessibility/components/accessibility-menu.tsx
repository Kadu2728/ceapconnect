"use client";

import { Accessibility } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  applyPreferences,
  readStoredPreferences,
  STORAGE_KEY,
  type AccessibilityPreferences,
  type TextSize,
} from "@/features/accessibility/lib/preferences";
import { cn } from "@/lib/utils";

const TEXT_SIZES: { value: TextSize; label: string }[] = [
  { value: "default", label: "Padrão" },
  { value: "large", label: "Grande" },
  { value: "xlarge", label: "Maior" },
];

/**
 * Menu de acessibilidade (EPIC 21): leitura facilitada, tamanho do texto e
 * alto contraste. As preferências viram atributos `data-*` no `<html>` e são
 * persistidas — o efeito visual é todo CSS, sem custo de runtime nas telas.
 */
export function AccessibilityMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const [preferences, setPreferences] = useState<AccessibilityPreferences | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // As preferências já foram aplicadas ao `<html>` pelo script inline do
  // layout — aqui só precisamos delas para desenhar o estado dos controles,
  // então lemos ao abrir o menu, e não a cada carregamento de página.
  function handleToggleMenu() {
    if (!isOpen && preferences === null) setPreferences(readStoredPreferences());
    setIsOpen((open) => !open);
  }

  useEffect(() => {
    if (!isOpen) return;

    function handlePointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) setIsOpen(false);
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setIsOpen(false);
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  function update(patch: Partial<AccessibilityPreferences>) {
    if (!preferences) return;
    const next = { ...preferences, ...patch };
    setPreferences(next);
    applyPreferences(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }

  return (
    <div ref={containerRef} className="relative">
      <Button
        variant="ghost"
        size="icon"
        aria-label="Opções de acessibilidade"
        aria-expanded={isOpen}
        aria-haspopup="dialog"
        onClick={handleToggleMenu}
      >
        <Accessibility className="size-5" aria-hidden="true" />
      </Button>

      {isOpen && preferences ? (
        <div
          role="dialog"
          aria-label="Opções de acessibilidade"
          className="absolute right-0 z-50 mt-2 w-64 rounded-xl border bg-popover p-4 text-popover-foreground shadow-lg"
        >
          <fieldset className="mb-4">
            <legend className="mb-2 text-sm font-semibold">Tamanho do texto</legend>
            <div className="flex gap-1.5">
              {TEXT_SIZES.map((size) => (
                <button
                  key={size.value}
                  type="button"
                  aria-pressed={preferences.textSize === size.value}
                  onClick={() => update({ textSize: size.value })}
                  className={cn(
                    "flex-1 rounded-md border px-2 py-1.5 text-xs font-medium transition-colors",
                    preferences.textSize === size.value
                      ? "border-primary bg-primary text-primary-foreground"
                      : "hover:bg-accent",
                  )}
                >
                  {size.label}
                </button>
              ))}
            </div>
          </fieldset>

          <label className="flex cursor-pointer items-start gap-2.5 py-2">
            <input
              type="checkbox"
              checked={preferences.readable}
              onChange={(event) => update({ readable: event.target.checked })}
              className="mt-0.5 size-4 shrink-0 accent-primary"
            />
            <span>
              <span className="block text-sm font-medium">Leitura facilitada</span>
              <span className="block text-xs text-muted-foreground">
                Fonte e espaçamento pensados para dislexia.
              </span>
            </span>
          </label>

          <label className="flex cursor-pointer items-start gap-2.5 py-2">
            <input
              type="checkbox"
              checked={preferences.contrast === "high"}
              onChange={(event) =>
                update({ contrast: event.target.checked ? "high" : "default" })
              }
              className="mt-0.5 size-4 shrink-0 accent-primary"
            />
            <span>
              <span className="block text-sm font-medium">Alto contraste</span>
              <span className="block text-xs text-muted-foreground">
                Reforça texto, bordas e foco.
              </span>
            </span>
          </label>
        </div>
      ) : null}
    </div>
  );
}
