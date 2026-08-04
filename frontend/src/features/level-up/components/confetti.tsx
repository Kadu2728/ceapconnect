"use client";

import { motion } from "framer-motion";

/** Cores de marca (theme-aware via CSS vars) usadas nos pedaços de confete. */
const COLORS = [
  "var(--brand)",
  "var(--brand-green)",
  "var(--brand-purple)",
  "var(--brand-orange)",
  "var(--brand-2)",
];

const PIECE_COUNT = 70;

interface ConfettiPiece {
  id: number;
  left: number;
  delay: number;
  duration: number;
  drift: number;
  rotate: number;
  color: string;
  size: number;
  round: boolean;
}

/**
 * Pedaços gerados uma única vez em escopo de módulo (fora do render): mantém o
 * render puro — nada de `Math.random()` durante a renderização — e o padrão,
 * ainda que fixo, parece aleatório. A animação de queda toca do zero a cada
 * montagem, então cada comemoração é visualmente nova.
 */
const PIECES: ConfettiPiece[] = Array.from({ length: PIECE_COUNT }, (_, id) => ({
  id,
  left: Math.random() * 100,
  delay: Math.random() * 0.5,
  duration: 2.2 + Math.random() * 1.8,
  drift: (Math.random() - 0.5) * 180,
  rotate: Math.random() * 720 - 360,
  color: COLORS[id % COLORS.length]!,
  size: 6 + Math.random() * 8,
  round: Math.random() > 0.5,
}));

/**
 * Chuva de confete comemorativa — pura (Framer Motion + CSS vars de marca), sem
 * biblioteca externa. `pointer-events-none` para nunca bloquear os botões do
 * modal por baixo.
 */
export function Confetti() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-[70] overflow-hidden"
    >
      {PIECES.map((piece) => (
        <motion.span
          key={piece.id}
          initial={{ y: "-10vh", opacity: 1 }}
          animate={{
            y: "110vh",
            x: piece.drift,
            rotate: piece.rotate,
            opacity: [1, 1, 0],
          }}
          transition={{ duration: piece.duration, delay: piece.delay, ease: "easeIn" }}
          style={{
            position: "absolute",
            left: `${piece.left}%`,
            width: piece.size,
            height: piece.size,
            background: piece.color,
            borderRadius: piece.round ? "9999px" : "2px",
          }}
        />
      ))}
    </div>
  );
}
