import { CalendarDays, Sparkles } from "lucide-react";

import { Card } from "@/components/ui/card";
import { formatFullDate } from "@/features/dashboard/utils/date";
import type { Profile } from "@/features/profile/types/profile.types";
import { getInitials } from "@/lib/text";

interface ProfileHeaderProps {
  profile: Profile;
}

/**
 * Cabeçalho do perfil: avatar com iniciais, nome, e-mail, nível atual e desde
 * quando o candidato faz parte. Dá identidade e um "resumo de quem é" logo no topo.
 */
export function ProfileHeader({ profile }: ProfileHeaderProps) {
  const { level } = profile.stats;

  return (
    <Card className="relative overflow-hidden border-brand/20 bg-gradient-to-br from-brand/10 via-background to-brand-green/10">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-16 -top-16 size-52 rounded-full bg-brand/10 blur-3xl"
      />
      <div className="relative flex flex-col items-center gap-4 px-6 text-center sm:flex-row sm:items-center sm:text-left">
        <span className="flex size-20 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand to-brand-green text-2xl font-bold text-primary-foreground shadow-lg shadow-brand/25">
          {getInitials(profile.name)}
        </span>

        <div className="min-w-0 flex-1">
          <h2 className="truncate text-xl font-bold tracking-tight">{profile.name}</h2>
          <p className="truncate text-sm text-muted-foreground">{profile.email}</p>

          <div className="mt-2 flex flex-wrap items-center justify-center gap-2 sm:justify-start">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-brand/10 px-3 py-1 text-sm font-semibold text-brand">
              <Sparkles className="size-3.5" aria-hidden="true" />
              Nível {level.level} · {level.name}
            </span>
            <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
              <CalendarDays className="size-3.5" aria-hidden="true" />
              Membro desde {formatFullDate(profile.member_since)}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
