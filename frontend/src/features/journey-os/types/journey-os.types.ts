/**
 * Contratos do Candidate Journey OS (`GET /candidate-state`,
 * `GET /next-best-action`, `POST /candidate-state/events`), espelhando o
 * contrato do backend. `momentum` nunca deve ser renderizado como texto cru
 * na UI — é o mecanismo de decisão (gate do Modo Resgate), não um rótulo
 * para o candidato ler.
 */

export type CandidateMomentum = "fluid" | "stable" | "friction" | "stalled" | "recovery";

/** Motivos da pausa — opções fechadas, nunca texto livre (o público inclui menores). */
export type PauseReasonCode = "trabalho" | "tempo" | "outro";

/**
 * Pausa declarada em curso ("Jornada que Respira"). Campo à parte de
 * `momentum` de propósito: momentum é *inferido* de comportamento, pausa é um
 * fato *declarado* pelo candidato. Quando presente, tem precedência — a
 * experiência para de cobrar avanço.
 */
export interface PauseState {
  ends_at: string;
  reason_code: PauseReasonCode | null;
  resume_action_key: string | null;
}

export interface CandidateState {
  version: string;
  computed_at: string;
  momentum: CandidateMomentum;
  current_step_key: string;
  days_since_last_activity: number;
  pending_required_documents: number;
  days_to_exam: number | null;
  guardian_training_overdue: boolean;
  pause: PauseState | null;
}

export interface PauseStartRequest {
  days: number;
  reason_code?: PauseReasonCode | null;
}

export interface PauseResumeResult {
  resumed: boolean;
  resume_action_key: string | null;
}

export type NextBestActionKey =
  "upload_documents" | "remind_guardian" | "prepare_for_exam" | "resume_journey";

export interface NextBestAction {
  action_key: NextBestActionKey;
  cta_label: string;
  why: string[];
}

/** Subconjunto de `ActivityEventName` que o próprio cliente pode disparar. */
export type CandidateTrackableEvent =
  | "nba_clicked"
  | "step_resumed"
  | "recovery_entered"
  | "recovery_completed"
  | "recovery_exited";
