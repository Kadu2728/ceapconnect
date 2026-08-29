"use client";

import { CalendarClock, CheckCircle2, FileWarning, MapPin } from "lucide-react";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { JourneyProgress } from "@/features/dashboard/components/journey-progress";
import { formatFullDate } from "@/features/dashboard/utils/date";
import type { GuardianChildJourneyResponse } from "@/features/guardian-access/types/guardian-access.types";

interface GuardianChildJourneyViewProps {
  data: GuardianChildJourneyResponse;
}

/**
 * Jornada essencial de um filho, do ponto de vista do responsável — só
 * progresso e pendências concretas (freio de privacidade do brief:
 * `GuardianChildJourneyResponse` estruturalmente não tem campo de risco).
 */
export function GuardianChildJourneyView({ data }: GuardianChildJourneyViewProps) {
  return (
    <div className="flex flex-col gap-6">
      <JourneyProgress journey={data.journey} />

      {data.pending_required_documents > 0 ? (
        <DashboardCard className="flex items-center gap-3">
          <FileWarning className="size-5 shrink-0 text-warning" aria-hidden="true" />
          <p className="text-sm">
            <span className="font-medium">
              {data.pending_required_documents}{" "}
              {data.pending_required_documents === 1
                ? "documento pendente"
                : "documentos pendentes"}
            </span>{" "}
            de envio — vale conferir com {data.candidate_name.split(" ")[0]}.
          </p>
        </DashboardCard>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <DashboardCard className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <CalendarClock className="size-4 text-brand" aria-hidden="true" />
            <h2 className="text-sm font-semibold">Prova</h2>
          </div>
          {data.exam_date ? (
            <>
              <p className="text-sm font-medium">{formatFullDate(data.exam_date)}</p>
              <p className="flex items-start gap-1.5 text-xs text-muted-foreground">
                <MapPin className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
                {data.exam_location}
              </p>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Data ainda não definida.</p>
          )}
        </DashboardCard>

        <DashboardCard className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <CalendarClock className="size-4 text-brand" aria-hidden="true" />
            <h2 className="text-sm font-semibold">Entrevista</h2>
          </div>
          {data.interview_date ? (
            <>
              <p className="text-sm font-medium">{formatFullDate(data.interview_date)}</p>
              <p className="flex items-start gap-1.5 text-xs text-muted-foreground">
                <MapPin className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
                {data.interview_location}
              </p>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Data ainda não definida.</p>
          )}
        </DashboardCard>
      </div>

      <DashboardCard className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold">Formação obrigatória do responsável</h2>
        {data.guardian_training_date ? (
          <p className="text-sm text-muted-foreground">
            {formatFullDate(data.guardian_training_date)}
          </p>
        ) : (
          <p className="text-sm text-muted-foreground">Data ainda não definida.</p>
        )}
        {data.guardian_training_attended ? (
          <StatusBadge label="Presença confirmada no dia" />
        ) : data.guardian_training_confirmed ? (
          <StatusBadge label="Presença confirmada — aguardando o dia" />
        ) : (
          <p className="text-sm text-amber-600 dark:text-amber-400">
            Presença ainda não confirmada.
          </p>
        )}
      </DashboardCard>
    </div>
  );
}

function StatusBadge({ label }: { label: string }) {
  return (
    <p className="flex items-center gap-2 text-sm text-success">
      <CheckCircle2 className="size-4 shrink-0" aria-hidden="true" />
      {label}
    </p>
  );
}
