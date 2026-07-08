"use client";

import { animate, useInView, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

interface CountUpProps {
  value: number;
  suffix?: string;
  duration?: number;
}

/**
 * Anima a contagem de 0 até `value` quando o elemento entra na viewport (uma
 * única vez). Reforça a percepção de "números que importam" nas estatísticas
 * institucionais. Respeita `prefers-reduced-motion` (mostra o valor final
 * imediatamente).
 */
export function CountUp({ value, suffix = "", duration = 1.4 }: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const shouldReduceMotion = useReducedMotion();
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (!inView || shouldReduceMotion) return;

    const controls = animate(0, value, {
      duration,
      ease: "easeOut",
      onUpdate: (latest) => setDisplay(Math.round(latest)),
    });

    return () => controls.stop();
  }, [inView, shouldReduceMotion, value, duration]);

  // Com movimento reduzido, mostramos o valor final direto (sem animar).
  const shown = shouldReduceMotion ? value : display;

  return (
    <span ref={ref}>
      {shown}
      {suffix}
    </span>
  );
}
