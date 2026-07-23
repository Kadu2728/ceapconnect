"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

/**
 * Transição de página global. O `template.tsx` do Next é re-montado a cada
 * navegação, então este fade de entrada roda em toda troca de rota.
 *
 * Anima **apenas opacidade** de propósito: um `transform` no elemento raiz da
 * página criaria um "containing block" e quebraria o posicionamento `fixed`
 * (navbar sticky, bottom nav, bolha do assistente). `opacity` não tem esse
 * efeito. Respeita `prefers-reduced-motion`.
 */
export default function Template({ children }: { children: ReactNode }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: shouldReduceMotion ? 1 : 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: shouldReduceMotion ? 0 : 0.25, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}
