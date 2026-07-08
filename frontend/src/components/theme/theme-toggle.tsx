"use client";

import { Monitor, Moon, Sun, type LucideIcon } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";
import { useHasMounted } from "@/hooks/use-has-mounted";
import { cn } from "@/lib/utils";

type ThemeOption = "light" | "dark" | "system";

const THEME_ICON: Record<ThemeOption, LucideIcon> = {
  light: Sun,
  dark: Moon,
  system: Monitor,
};

const THEME_LABEL: Record<ThemeOption, string> = {
  light: "Tema claro ativo. Alternar para tema escuro.",
  dark: "Tema escuro ativo. Alternar para tema automático.",
  system: "Tema automático ativo. Alternar para tema claro.",
};

// light -> dark -> system -> light
const NEXT_THEME: Record<ThemeOption, ThemeOption> = {
  light: "dark",
  dark: "system",
  system: "light",
};

interface ThemeToggleProps {
  className?: string;
}

/**
 * Alterna entre tema claro, escuro e automático (sistema).
 *
 * Decisão de UX: um botão único com ciclo de 3 estados (em vez de um menu
 * dropdown) reduz o número de toques em mobile para a ação mais frequente
 * de configuração — troca de tema.
 */
export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, setTheme } = useTheme();
  const mounted = useHasMounted();

  if (!mounted) {
    return (
      <Button
        variant="outline"
        size="icon"
        className={cn("size-9", className)}
        disabled
        aria-hidden
      />
    );
  }

  const current = (theme as ThemeOption | undefined) ?? "system";
  const Icon = THEME_ICON[current];

  const handleClick = () => {
    setTheme(NEXT_THEME[current]);
  };

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={handleClick}
      aria-label={THEME_LABEL[current]}
      className={cn("size-9", className)}
    >
      <Icon className="size-4" />
    </Button>
  );
}
