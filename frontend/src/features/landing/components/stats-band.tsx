import { CountUp } from "@/components/motion/count-up";
import { Reveal } from "@/components/motion/reveal";
import { STATS } from "@/features/landing/data/stats";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import { cn } from "@/lib/utils";

/**
 * Faixa de prova social com indicadores institucionais do CEAP. Números
 * animam com contagem crescente ao entrar na viewport (ver `CountUp`).
 */
export function StatsBand() {
  return (
    <section className="border-y border-border/60 bg-muted/30">
      <div
        className={cn(
          LANDING_CONTAINER_CLASS,
          "grid grid-cols-2 gap-x-6 gap-y-8 py-12 sm:py-14 lg:grid-cols-4",
        )}
      >
        {STATS.map((stat, index) => (
          <Reveal key={stat.label} delay={index * 0.08} className="text-center">
            <div className="text-4xl font-bold tracking-tight text-brand sm:text-5xl">
              {typeof stat.value === "number" ? (
                <CountUp value={stat.value} suffix={stat.suffix} />
              ) : (
                stat.display
              )}
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{stat.label}</p>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
