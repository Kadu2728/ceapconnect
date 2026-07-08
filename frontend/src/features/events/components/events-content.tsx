"use client";

import { motion, useReducedMotion } from "framer-motion";
import { CalendarX } from "lucide-react";

import { EventCard } from "@/features/events/components/event-card";
import { useEventRegistration } from "@/features/events/hooks/use-event-registration";
import type { EventList } from "@/features/events/types/event.types";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface EventsContentProps {
  data: EventList;
}

/**
 * Composição da tela de Eventos: lista de eventos com entrada escalonada.
 * Detém a mutation de inscrição/cancelamento e a repassa a cada card. Exibe um
 * estado vazio amigável quando não há eventos futuros.
 */
export function EventsContent({ data }: EventsContentProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  const { mutate, isPending, variables } = useEventRegistration();

  if (data.events.length === 0) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 text-center">
        <span className="flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <CalendarX className="size-6" aria-hidden="true" />
        </span>
        <div>
          <h2 className="font-semibold">Nenhum evento por enquanto</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Novos eventos aparecerão aqui assim que forem agendados.
          </p>
        </div>
      </div>
    );
  }

  return (
    <motion.ul
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="flex flex-col gap-4"
    >
      {data.events.map((event) => (
        <motion.li key={event.id} variants={itemVariants}>
          <EventCard
            event={event}
            onToggle={() => mutate({ eventId: event.id, registered: event.registered })}
            isPending={isPending && variables?.eventId === event.id}
          />
        </motion.li>
      ))}
    </motion.ul>
  );
}
