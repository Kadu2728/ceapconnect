"use client";

import { Share2 } from "lucide-react";
import { useState } from "react";

import { toast } from "@/components/feedback/toast/toast-store";
import { Button } from "@/components/ui/button";
import type { Achievement } from "@/features/achievements/types/achievement.types";
import { shareAchievement } from "@/features/achievements/utils/share-achievement";

interface ShareAchievementButtonProps {
  achievement: Achievement;
}

/**
 * Compartilha uma conquista desbloqueada. É o único pedaço client-side do card
 * de conquista — o resto continua sendo Server Component.
 */
export function ShareAchievementButton({ achievement }: ShareAchievementButtonProps) {
  const [isSharing, setIsSharing] = useState(false);

  async function handleShare() {
    setIsSharing(true);
    try {
      const result = await shareAchievement(achievement);
      if (result === "copied") {
        toast.success("Texto copiado!", {
          description: "Cole onde quiser para compartilhar sua conquista.",
        });
      }
    } catch {
      toast.error("Não foi possível compartilhar agora.");
    } finally {
      setIsSharing(false);
    }
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleShare}
      disabled={isSharing}
      aria-label={`Compartilhar conquista ${achievement.name}`}
    >
      <Share2 className="size-4" aria-hidden="true" />
      Compartilhar
    </Button>
  );
}
