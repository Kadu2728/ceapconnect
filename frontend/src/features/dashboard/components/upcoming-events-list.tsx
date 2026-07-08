import { CalendarDays, MapPin } from "lucide-react";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { InlineEmptyState } from "@/features/dashboard/components/inline-empty-state";
import type { DashboardEvent } from "@/features/dashboard/types/dashboard.types";
import { formatEventDate } from "@/features/dashboard/utils/date";

interface UpcomingEventsListProps {
  events: DashboardEvent[];
}

/** Lista dos próximos eventos do processo seletivo (EPIC 03). */
export function UpcomingEventsList({ events }: UpcomingEventsListProps) {
  return (
    <DashboardCard>
      <h2 className="text-base font-semibold">Próximos eventos</h2>

      {events.length === 0 ? (
        <InlineEmptyState
          icon={CalendarDays}
          message="Nenhum evento agendado no momento."
        />
      ) : (
        <ul className="mt-5 flex flex-col gap-4">
          {events.map((event) => (
            <li key={event.id} className="flex items-start gap-3">
              <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
                <CalendarDays className="size-4" aria-hidden="true" />
              </span>
              <div className="flex flex-col">
                <span className="text-sm font-medium">{event.title}</span>
                <span className="text-xs text-muted-foreground">
                  {formatEventDate(event.date)}
                </span>
                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                  <MapPin className="size-3" aria-hidden="true" />
                  {event.location}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </DashboardCard>
  );
}
