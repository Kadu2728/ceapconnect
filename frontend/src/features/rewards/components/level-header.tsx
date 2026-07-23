import { Sparkles, Trophy } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { LevelInfo } from "@/features/rewards/types/reward.types";

interface LevelHeaderProps {
  level: LevelInfo;
}

/**
 * "Herói" da gamificação: transforma o XP num nível legível e mostra, de forma
 * imediata, quanto falta para o próximo nível. É a resposta visual ao pedido de
 * deixar a progressão clara — número grande, rótulo do nível e barra de meta.
 */
export function LevelHeader({ level }: LevelHeaderProps) {
  const {
    level: levelNumber,
    name,
    xp_total: xpTotal,
    xp_to_next: xpToNext,
    progress_percentage: progress,
    is_max_level: isMaxLevel,
  } = level;

  return (
    <Card className="relative overflow-hidden border-brand/20 bg-gradient-to-br from-brand/10 via-background to-brand-green/10">
      {/* Brilho decorativo, puramente estético (não captura eventos). */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-16 -top-16 size-56 rounded-full bg-brand/10 blur-3xl"
      />

      <div className="relative flex flex-col gap-5 px-6 sm:flex-row sm:items-center sm:gap-6">
        <div className="flex items-center gap-4">
          <span className="flex size-16 shrink-0 flex-col items-center justify-center rounded-2xl bg-gradient-to-br from-brand to-brand-green text-primary-foreground shadow-lg shadow-brand/25">
            <span className="text-[0.625rem] font-semibold uppercase tracking-wide opacity-90">
              Nível
            </span>
            <span className="text-2xl font-bold leading-none">{levelNumber}</span>
          </span>

          <div className="min-w-0">
            <p className="text-sm text-muted-foreground">Seu nível atual</p>
            <h2 className="flex items-center gap-2 text-xl font-bold tracking-tight">
              {name}
              {isMaxLevel ? (
                <Trophy className="size-5 text-brand-orange" aria-hidden="true" />
              ) : null}
            </h2>
            <p className="mt-0.5 inline-flex items-center gap-1.5 text-sm font-medium text-brand">
              <Sparkles className="size-3.5" aria-hidden="true" />
              {xpTotal.toLocaleString("pt-BR")} XP acumulados
            </p>
          </div>
        </div>

        <div className="flex-1 sm:pl-4">
          {isMaxLevel ? (
            <p className="text-sm font-medium text-success">
              🏆 Nível máximo alcançado — você desbloqueou todas as recompensas por nível!
            </p>
          ) : (
            <>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Progresso do nível</span>
                <span className="font-semibold text-foreground">
                  Faltam {xpToNext?.toLocaleString("pt-BR")} XP
                </span>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-brand to-brand-green transition-[width] duration-700"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Complete missões para ganhar XP e subir de nível — cada nível libera novas
                recompensas.
              </p>
            </>
          )}
        </div>
      </div>
    </Card>
  );
}
