import type { SimuladoSubject } from "@/features/simulados/types/simulado.types";

/**
 * Rótulo em português de cada matéria do simulado — único lugar que conhece
 * essa tradução (antes duplicado em `simulado-runner.tsx` e
 * `simulado-result.tsx`; agora também usado por `simulado-history.tsx` para
 * a trilha de estudo).
 */
export const SUBJECT_LABEL: Record<SimuladoSubject, string> = {
  portugues: "Português",
  matematica: "Matemática",
};
