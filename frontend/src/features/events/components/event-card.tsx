import { CalendarClock, Check, MapPin } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { CommunityEvent } from "@/features/events/types/event.types";

function formatDateTime(iso: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

interface EventCardProps {
  event: CommunityEvent;
  onToggle: () => void;
  isPending: boolean;
}

/**
 * Card de um evento. Mostra data/hora, local e um selo "Inscrito" quando é o
 * caso; a ação alterna entre inscrever-se e cancelar conforme o estado atual.
 */
export function EventCard({ event, onToggle, isPending }: EventCardProps) {
  const { registered } = event;

  return (
    <Card className="gap-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-md">
      <div className="flex flex-col gap-3 px-6">
        <div className="flex items-center justify-between gap-3">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-brand capitalize">
            <CalendarClock className="size-3.5" aria-hidden="true" />
            {formatDateTime(event.date)}
          </span>
          {registered ? (
            <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-success/15 px-2.5 py-1 text-xs font-semibold text-success">
              <Check className="size-3" aria-hidden="true" />
              Inscrito
            </span>
          ) : null}
        </div>

        <div>
          <h3 className="font-semibold">{event.title}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{event.description}</p>
        </div>

        <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <MapPin className="size-4 shrink-0" aria-hidden="true" />
          {event.location}
        </p>
      </div>

      <div className="px-6">
        <Button
          variant={registered ? "outline" : "default"}
          size="sm"
          onClick={onToggle}
          disabled={isPending}
          className="w-full sm:w-auto"
        >
          {isPending
            ? "Processando…"
            : registered
              ? "Cancelar inscrição"
              : "Inscrever-se"}
        </Button>
      </div>
    </Card>
  );
}
