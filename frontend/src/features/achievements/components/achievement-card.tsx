import { Lock } from "lucide-react";
import { createElement } from "react";

import { Card } from "@/components/ui/card";
import type { Achievement } from "@/features/achievements/types/achievement.types";
import { resolveAchievementIcon } from "@/features/dashboard/utils/achievement-icons";
import { cn } from "@/lib/utils";

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(iso));
}

interface AchievementCardProps {
  achievement: Achievement;
}

/**
 * Card de uma conquista. Desbloqueada: ícone em destaque de marca + data.
 * Bloqueada: cadeado e tom esmaecido — comunica "há mais para conquistar" sem
 * esconder o objetivo (motivação, nunca frustração).
 */
export function AchievementCard({ achievement }: AchievementCardProps) {
  const { unlocked, unlocked_at: unlockedAt } = achievement;

  return (
    <Card className={cn("h-full gap-3 text-center", !unlocked && "opacity-70")}>
      <div className="flex flex-col items-center gap-3 px-6">
        <span
          className={cn(
            "flex size-14 items-center justify-center rounded-2xl",
            unlocked
              ? "bg-gradient-to-br from-brand/15 to-brand-green/15 text-brand"
              : "bg-muted text-muted-foreground",
          )}
        >
          {unlocked ? (
            createElement(resolveAchievementIcon(achievement.icon), {
              className: "size-7",
              "aria-hidden": true,
            })
          ) : (
            <Lock className="size-6" aria-hidden="true" />
          )}
        </span>

        <div>
          <h3 className={cn("font-semibold", !unlocked && "text-muted-foreground")}>
            {achievement.name}
          </h3>
          <p className="mt-1 text-sm text-muted-foreground">{achievement.description}</p>
        </div>

        <span
          className={cn(
            "mt-1 text-xs font-medium",
            unlocked ? "text-success" : "text-muted-foreground",
          )}
        >
          {unlocked && unlockedAt
            ? `Desbloqueada em ${formatDate(unlockedAt)}`
            : "Ainda não desbloqueada"}
        </span>
      </div>
    </Card>
  );
}
