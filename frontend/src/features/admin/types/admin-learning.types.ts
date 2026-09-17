/**
 * Contratos da gestão de cursos no painel admin (`/admin/learning/*`),
 * espelhando `app.schemas.admin_learning`.
 */

import type {
  CourseAudience,
  VideoProvider,
} from "@/features/learning/types/learning.types";

export interface AdminLesson {
  id: string;
  module_id: string;
  title: string;
  description: string | null;
  video_provider: VideoProvider;
  video_ref: string;
  duration_seconds: number;
  order: number;
  is_active: boolean;
}

export interface AdminModule {
  id: string;
  course_id: string;
  title: string;
  description: string | null;
  order: number;
  lessons: AdminLesson[];
}

export interface AdminCourse {
  id: string;
  slug: string;
  title: string;
  description: string;
  audience: CourseAudience;
  thumbnail_url: string | null;
  is_active: boolean;
  module_count: number;
  lesson_count: number;
  updated_at: string;
}

export interface AdminCourseDetail extends AdminCourse {
  modules: AdminModule[];
}

export interface AdminCourseList {
  courses: AdminCourse[];
  audiences: CourseAudience[];
  providers: VideoProvider[];
  completion_threshold: number;
}

export interface AdminCourseInput {
  slug: string;
  title: string;
  description: string;
  audience: CourseAudience;
  thumbnail_url: string | null;
  is_active: boolean;
}

export interface AdminModuleInput {
  title: string;
  description: string | null;
  order: number;
}

export interface AdminLessonInput {
  title: string;
  description: string | null;
  video_provider: VideoProvider;
  video_ref: string;
  duration_seconds: number;
  order: number;
  is_active: boolean;
}
