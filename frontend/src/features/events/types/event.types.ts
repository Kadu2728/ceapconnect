/**
 * Contratos da feature Eventos (EPIC 07), espelhando o backend
 * (`GET /api/v1/events`, `POST`/`DELETE /api/v1/events/{id}/register`).
 */

export interface CommunityEvent {
  id: string;
  title: string;
  description: string;
  date: string;
  location: string;
  image_url: string | null;
  registered: boolean;
}

export interface EventSummary {
  total: number;
  registered: number;
}

export interface EventList {
  events: CommunityEvent[];
  summary: EventSummary;
}

export interface EventRegistrationResult {
  event: CommunityEvent;
  registered: boolean;
}
