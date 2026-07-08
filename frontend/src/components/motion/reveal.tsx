"use client";

import { motion, useReducedMotion, type HTMLMotionProps } from "framer-motion";

const MOTION_TAGS = {
  div: motion.div,
  li: motion.li,
  ul: motion.ul,
  section: motion.section,
} as const;

type MotionTag = keyof typeof MOTION_TAGS;

type RevealProps<T extends MotionTag> = {
  as?: T;
  /** Atraso de entrada em segundos (para escalonar elementos irmãos). */
  delay?: number;
  /** Deslocamento vertical inicial em px (padrão 20). */
  y?: number;
} & Omit<HTMLMotionProps<T>, "ref">;

/**
 * Revela o conteúdo ao entrar na viewport (uma única vez), com fade + leve
 * deslocamento vertical. Centraliza o padrão de scroll-reveal usado em toda a
 * Landing Page e respeita `prefers-reduced-motion` (sem deslocamento/duração).
 *
 * Anima apenas `transform`/`opacity` (nunca layout) para manter 60fps. O `as`
 * é resolvido a partir de um mapa estático — nunca via `motion(Component)` no
 * corpo do render (evita remontagens).
 */
export function Reveal<T extends MotionTag = "div">({
  as,
  delay = 0,
  y = 20,
  children,
  ...props
}: RevealProps<T>) {
  const shouldReduceMotion = useReducedMotion();
  // Tipagem interna colapsada em `motion.div` — os props já são validados no
  // call site pelo genérico `RevealProps<T>`.
  const Component = MOTION_TAGS[(as ?? "div") as MotionTag] as typeof motion.div;

  return (
    <Component
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{
        duration: shouldReduceMotion ? 0 : 0.55,
        delay: shouldReduceMotion ? 0 : delay,
        ease: [0.22, 1, 0.36, 1],
      }}
      {...(props as HTMLMotionProps<"div">)}
    >
      {children}
    </Component>
  );
}
