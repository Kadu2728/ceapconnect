import { CalendarClock } from "lucide-react";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { formatFullDate, getDaysUntil } from "@/features/dashboard/utils/date";

interface ExamCountdownProps {
  examDate: string | null;
}

/**
 * Contagem regressiva até o dia da prova (EPIC 03). `exam_date` nulo (ainda
 * não definida) ou inválido recebe um estado neutro em vez de um countdown
 * quebrado — nunca "NaN dias" ou similar na tela.
 */
export function ExamCountdown({ examDate }: ExamCountdownProps) {
  const daysRemaining = examDate ? getDaysUntil(examDate) : null;

  if (!examDate || daysRemaining === null) {
    return (
      <DashboardCard className="flex items-center gap-4">
        <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <CalendarClock className="size-6" aria-hidden="true" />
        </span>
        <div>
          <h2 className="text-sm font-semibold">Data da prova</h2>
          <p className="text-sm text-muted-foreground">
            Ainda não definida. Assim que for confirmada, ela aparece aqui.
          </p>
        </div>
      </DashboardCard>
    );
  }

  const isPast = daysRemaining < 0;
  const isToday = daysRemaining === 0;

  return (
    <DashboardCard className="flex items-center gap-4">
      <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
        <CalendarClock className="size-6" aria-hidden="true" />
      </span>
      <div>
        <h2 className="text-sm font-semibold">Data da prova</h2>
        {isPast ? (
          <p className="text-sm text-muted-foreground">
            Prova realizada em {formatFullDate(examDate)}.
          </p>
        ) : isToday ? (
          <p className="text-sm font-semibold text-primary">
            É hoje! {formatFullDate(examDate)}.
          </p>
        ) : (
          <p className="text-sm text-muted-foreground">
            Faltam <span className="font-semibold text-foreground">{daysRemaining}</span>{" "}
            {daysRemaining === 1 ? "dia" : "dias"} · {formatFullDate(examDate)}
          </p>
        )}
      </div>
    </DashboardCard>
  );
}
