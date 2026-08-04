"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { Confetti } from "@/features/level-up/components/confetti";

interface Celebration {
  level: number;
  name: string;
}

interface Tracked {
  /** Usuário a quem o nível observado pertence (evita falso disparo ao trocar de conta). */
  userId: string;
  level: number;
}

/**
 * Vigia de nível + comemoração de level-up. Montado uma vez no shell autenticado.
 *
 * Observa o nível vindo do Dashboard (cache compartilhado do react-query) e,
 * quando ele aumenta para o usuário atual, abre um modal com confete. A detecção
 * usa o padrão do React de "ajustar estado durante o render" (sem efeito, sem
 * re-render em cascata): compara o nível atual ao último registrado e converge
 * assim que sincroniza. Ignora a primeira leitura (inicializa sem comemorar) e é
 * por usuário.
 */
export function LevelUpCelebration() {
  const userId = useAuthStore((state) => state.user?.id);
  const { data } = useDashboard();
  const currentLevel = data?.level.level;
  const currentName = data?.level.name;

  const [tracked, setTracked] = useState<Tracked | null>(null);
  const [celebration, setCelebration] = useState<Celebration | null>(null);
  const shouldReduceMotion = Boolean(useReducedMotion());

  if (userId && currentLevel !== undefined && currentName !== undefined) {
    if (tracked?.userId !== userId) {
      // Primeira leitura para este usuário: apenas registra, sem comemorar.
      setTracked({ userId, level: currentLevel });
    } else if (currentLevel > tracked.level) {
      setTracked({ userId, level: currentLevel });
      setCelebration({ level: currentLevel, name: currentName });
    } else if (currentLevel !== tracked.level) {
      // Nível caiu (ex.: ajuste administrativo): só sincroniza, sem comemorar.
      setTracked({ userId, level: currentLevel });
    }
  }

  const close = useCallback(() => setCelebration(null), []);

  useEffect(() => {
    if (celebration === null) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [celebration, close]);

  return (
    <AnimatePresence>
      {celebration !== null ? (
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-label="Você subiu de nível"
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <button
            type="button"
            aria-label="Fechar"
            onClick={close}
            className="absolute inset-0 cursor-default bg-black/50 backdrop-blur-sm"
          />

          {!shouldReduceMotion ? <Confetti /> : null}

          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 12 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 22 }}
            className="relative z-10 w-full max-w-sm overflow-hidden rounded-2xl border bg-card p-6 text-center shadow-xl"
          >
            <button
              type="button"
              aria-label="Fechar"
              onClick={close}
              className="absolute right-3 top-3 flex size-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
            >
              <X className="size-4" aria-hidden="true" />
            </button>

            <motion.span
              initial={{ scale: 0.6, rotate: -12 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.1, type: "spring", stiffness: 240, damping: 14 }}
              className="mx-auto flex size-20 flex-col items-center justify-center rounded-full bg-gradient-to-br from-brand to-brand-green text-primary-foreground shadow-lg shadow-brand/30"
            >
              <span className="text-[0.625rem] font-semibold uppercase tracking-wide opacity-90">
                Nível
              </span>
              <span className="text-3xl font-bold leading-none">{celebration.level}</span>
            </motion.span>

            <h2 className="mt-4 flex items-center justify-center gap-1.5 text-xl font-bold tracking-tight">
              <Sparkles className="size-5 text-brand-orange" aria-hidden="true" />
              Você subiu de nível!
            </h2>
            <p className="mt-1 text-muted-foreground">
              Agora você é{" "}
              <span className="font-semibold text-foreground">{celebration.name}</span>.
              Continue avançando para desbloquear novas recompensas.
            </p>

            <div className="mt-6 flex flex-col gap-2">
              <Button asChild onClick={close}>
                <Link href="/recompensas">
                  Ver recompensas
                  <ArrowRight className="size-4" aria-hidden="true" />
                </Link>
              </Button>
              <Button variant="ghost" onClick={close}>
                Continuar
              </Button>
            </div>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
