/**
 * Contratos dos Simulados de prova (EPIC 16), espelhando o backend
 * (`/api/v1/simulados`). Campos em `snake_case` como o backend os envia.
 */

export type SimuladoSubject = "portugues" | "matematica";

export interface QuestionOption {
  key: string;
  text: string;
}

export interface SimuladoQuestion {
  id: string;
  subject: SimuladoSubject;
  statement: string;
  options: QuestionOption[];
}

export interface StartAttemptResult {
  attempt_id: string;
  questions: SimuladoQuestion[];
}

export interface AnswerResult {
  question_id: string;
  is_correct: boolean;
  correct_option_key: string;
  explanation: string;
}

export interface SubjectBreakdown {
  subject: SimuladoSubject;
  correct: number;
  total: number;
}

export interface FinishAttemptResult {
  attempt_id: string;
  correct_count: number;
  total_questions: number;
  score_percentage: number;
  subject_breakdown: SubjectBreakdown[];
  xp_awarded: number;
  /** Matéria com menor taxa de acerto nesta tentativa; `null` = sem dado suficiente. */
  weakest_subject: SimuladoSubject | null;
}

export interface AttemptHistoryItem {
  attempt_id: string;
  finished_at: string;
  correct_count: number;
  total_questions: number;
  score_percentage: number;
}

export interface AttemptHistory {
  attempts: AttemptHistoryItem[];
  best_score_percentage: number | null;
  /** Matéria com menor taxa de acerto em todo o histórico; `null` = sem dado suficiente. */
  weakest_subject: SimuladoSubject | null;
}
