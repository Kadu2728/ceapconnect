import type { Variants } from "framer-motion";

/**
 * Variants de entrada com stagger sutil, para seções que revelam uma lista
 * de itens em sequência (hoje: Dashboard; o mesmo padrão já existe duplicado
 * em `Hero` e `Pillars` da Landing Page — candidatos a migrar para cá em uma
 * limpeza futura, fora do escopo desta mudança).
 *
 * Recebem `shouldReduceMotion` explicitamente porque um objeto `Variants` não
 * pode chamar hooks — quem invoca decide o valor via `useReducedMotion()`.
 */
export function getStaggerContainerVariants(shouldReduceMotion: boolean): Variants {
  return {
    hidden: {},
    visible: { transition: { staggerChildren: shouldReduceMotion ? 0 : 0.08 } },
  };
}

export function getStaggerItemVariants(shouldReduceMotion: boolean): Variants {
  return {
    hidden: { opacity: 0, y: shouldReduceMotion ? 0 : 12 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: shouldReduceMotion ? 0 : 0.4, ease: "easeOut" },
    },
  };
}
