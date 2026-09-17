/**
 * Contratos do módulo de Videoaulas, espelhando `app.schemas.learning`.
 *
 * `CourseOverview` nunca traz `video_ref` — só `LessonDetail`, quando a
 * pessoa abre a aula. É a garantia estrutural de que a página "Formação de
 * Pais" carrega leve, sem vídeo nenhum.
 */

export type CourseAudience = "guardian" | "candidate";
export type VideoProvider = "url";
export type LessonStatus = "available" | "in_progress" | "completed";

export interface LessonSummary {
  id: string;
  title: string;
  description: string | null;
  duration_seconds: number;
  order: number;
  status: LessonStatus;
  watched_percent: number;
  resume_position_seconds: number;
}

export interface ModuleSummary {
  id: string;
  title: string;
  description: string | null;
  order: number;
  lessons: LessonSummary[];
  completed_count: number;
}

export interface CourseCard {
  id: string;
  slug: string;
  title: string;
  description: string;
  audience: CourseAudience;
  thumbnail_url: string | null;
}

export interface CourseOverview {
  course: CourseCard;
  modules: ModuleSummary[];
  total_lessons: number;
  completed_lessons: number;
  progress_percent: number;
  next_lesson: LessonSummary | null;
}

export interface LessonDetail {
  id: string;
  course_slug: string;
  course_title: string;
  module_title: string;
  title: string;
  description: string | null;
  video_provider: VideoProvider;
  video_ref: string;
  duration_seconds: number;
  status: LessonStatus;
  resume_position_seconds: number;
  previous_lesson_id: string | null;
  next_lesson_id: string | null;
}

export interface ProgressUpdateResult {
  lesson_id: string;
  status: LessonStatus;
  watched_percent: number;
  resume_position_seconds: number;
  completed_at: string | null;
  just_completed: boolean;
}
