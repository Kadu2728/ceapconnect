"use client";

import { ChevronRight, UserRound } from "lucide-react";
import Link from "next/link";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import type { GuardianChildItem } from "@/features/guardian-access/types/guardian-access.types";

interface GuardianChildrenListProps {
  items: GuardianChildItem[];
}

/**
 * Lista dos filhos vinculados e autorizados à conta do responsável — nunca
 * mostra nada de risco, só o rótulo da etapa atual e o percentual de
 * progresso (mesmo corte de privacidade do backend, `GuardianChildItem`).
 */
export function GuardianChildrenList({ items }: GuardianChildrenListProps) {
  if (items.length === 0) {
    return (
      <DashboardCard className="flex flex-col items-center gap-2 py-10 text-center">
        <UserRound className="size-8 text-muted-foreground" aria-hidden="true" />
        <p className="font-medium">Nenhum candidato vinculado ainda</p>
        <p className="max-w-sm text-sm text-muted-foreground">
          Use o link enviado por e-mail ou WhatsApp pelo candidato para vincular a jornada
          dele à sua conta.
        </p>
      </DashboardCard>
    );
  }

  return (
    <ul className="flex flex-col gap-3">
      {items.map((child) => (
        <li key={child.candidate_profile_id}>
          <Link
            href={`/area-responsavel/${child.candidate_profile_id}`}
            className="flex items-center gap-4 rounded-2xl border bg-card p-5 shadow-sm transition-colors hover:bg-accent/40"
          >
            <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
              <UserRound className="size-5" aria-hidden="true" />
            </span>
            <div className="flex-1">
              <p className="font-semibold">{child.name}</p>
              <p className="text-sm text-muted-foreground">{child.current_step_label}</p>
            </div>
            <span className="text-sm font-semibold text-primary">
              {child.journey_percentage}%
            </span>
            <ChevronRight
              className="size-4 shrink-0 text-muted-foreground"
              aria-hidden="true"
            />
          </Link>
        </li>
      ))}
    </ul>
  );
}
