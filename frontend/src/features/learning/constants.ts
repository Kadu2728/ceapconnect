/**
 * Rotas e chaves do módulo de Videoaulas na Área do Responsável.
 *
 * Centralizadas para a navegação (`GuardianShell`), o card da home e as
 * páginas apontarem para o mesmo lugar — trocar a URL é uma linha aqui.
 */

/** Slug do curso da Formação de Pais (o seed cria com esta chave). */
export const GUARDIAN_COURSE_SLUG = "formacao-de-pais";

export const GUARDIAN_LEARNING_ROUTES = {
  course: "/area-responsavel/formacao",
  lesson: (lessonId: string) => `/area-responsavel/formacao/aula/${lessonId}`,
} as const;
