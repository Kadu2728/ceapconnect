/**
 * Rotas e chaves do módulo de Videoaulas — uma entrada por público.
 *
 * As páginas, a navegação e os cards apontam para o mesmo lugar por aqui;
 * trocar uma URL é uma linha. `LearningRoutes` é o contrato que os
 * componentes de feature (`CourseOverviewView`, `LessonView`) recebem: eles
 * não sabem em qual área estão — só para onde levar cada aula.
 */

export interface LearningRoutes {
  /** Dashboard do curso (progresso + módulos). */
  course: string;
  /** Página de uma aula. */
  lesson: (lessonId: string) => string;
}

/** Slug do curso da Formação de Pais (o seed cria com esta chave). */
export const GUARDIAN_COURSE_SLUG = "formacao-de-pais";

export const GUARDIAN_LEARNING_ROUTES: LearningRoutes = {
  course: "/area-responsavel/formacao",
  lesson: (lessonId) => `/area-responsavel/formacao/aula/${lessonId}`,
};

/** Slug do curso de preparação do candidato (o seed cria com esta chave). */
export const CANDIDATE_COURSE_SLUG = "preparacao-para-a-prova";

export const CANDIDATE_LEARNING_ROUTES: LearningRoutes = {
  course: "/aulas",
  lesson: (lessonId) => `/aulas/${lessonId}`,
};
