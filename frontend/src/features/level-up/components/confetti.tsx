/** Cores de marca (theme-aware via CSS vars) usadas nos pedaços de confete. */
const COLORS = [
  "var(--brand)",
  "var(--brand-green)",
  "var(--brand-purple)",
  "var(--brand-orange)",
  "var(--brand-2)",
];

/**
 * 36 pedaços: o suficiente para a tela parecer cheia, metade do custo de
 * renderização do valor anterior (70). O público usa muito celular de entrada
 * — a comemoração não pode engasgar justamente no momento de recompensa.
 */
const PIECE_COUNT = 36;

/**
 * Padrão gerado uma única vez em escopo de módulo (fora do render): mantém o
 * render puro — nada de `Math.random()` durante a renderização — e o padrão,
 * ainda que fixo, parece aleatório.
 */
const PIECES = Array.from({ length: PIECE_COUNT }, (_, id) => ({
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
 * Chuva de confete comemorativa em CSS puro — sem biblioteca e sem JavaScript
 * de animação: são só `transform` e `opacity`, compostos pela GPU, então nem
 * o main thread nem o layout são tocados enquanto cai. Antes eram 70
 * `motion.span` do Framer Motion animando ao mesmo tempo.
 *
 * Sem `"use client"` porque não precisa de nada do cliente (é markup puro);
 * na prática entra na árvore client via `LevelUpCelebration`, que é quem
 * decide exibi-lo e já respeita `prefers-reduced-motion`.
 */
export function Confetti() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-[70] overflow-hidden"
    >
      <style>{`
        @keyframes ceap-confetti-fall {
          from { transform: translate3d(0, -10vh, 0) rotate(0deg); opacity: 1; }
          to   { transform: translate3d(var(--drift), 110vh, 0) rotate(var(--rotate)); opacity: 0; }
        }
      `}</style>

      {PIECES.map((piece) => (
        <span
          key={piece.id}
          style={{
            position: "absolute",
            top: 0,
            left: `${piece.left}%`,
            width: piece.size,
            height: piece.size,
            background: piece.color,
            borderRadius: piece.round ? "9999px" : "2px",
            willChange: "transform, opacity",
            ["--drift" as string]: `${piece.drift}px`,
            ["--rotate" as string]: `${piece.rotate}deg`,
            animation: `ceap-confetti-fall ${piece.duration}s ease-in ${piece.delay}s forwards`,
          }}
        />
      ))}
    </div>
  );
}
