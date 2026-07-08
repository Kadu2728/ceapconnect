import { Reveal } from "@/components/motion/reveal";
import { SectionHeading } from "@/features/landing/components/section-heading";
import { JOURNEY_STAGES } from "@/features/landing/data/journey";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import { cn } from "@/lib/utils";

/**
 * Trilha vertical da jornada do candidato. Formato de timeline numerada,
 * naturalmente mobile-first e legível em qualquer largura, com uma linha em
 * gradiente de marca conectando as etapas. Cada etapa entra em sequência ao
 * rolar (ver `Reveal`).
 */
export function JourneySection() {
  return (
    <section className="border-y border-border/60 bg-muted/20 py-20 sm:py-24">
      <div className={LANDING_CONTAINER_CLASS}>
        <SectionHeading
          eyebrow="Sua jornada"
          title="Cada etapa, no seu tempo"
          description="Do primeiro clique ao resultado, você sempre sabe onde está e qual é o próximo passo."
        />

        <ol className="relative mx-auto mt-14 max-w-2xl">
          <span
            aria-hidden="true"
            className="absolute top-3 bottom-3 left-5 w-px bg-gradient-to-b from-brand via-brand-green to-transparent"
          />

          {JOURNEY_STAGES.map((stage, index) => (
            <Reveal
              as="li"
              key={stage.title}
              delay={index * 0.06}
              className="relative flex gap-5 pb-9 last:pb-0"
            >
              <span
                className={cn(
                  "relative z-10 flex size-10 shrink-0 items-center justify-center rounded-full",
                  "border border-border/70 bg-background text-sm font-semibold text-brand shadow-sm",
                )}
              >
                {index + 1}
              </span>

              <div className="pt-1.5">
                <h3 className="font-semibold text-foreground">{stage.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{stage.description}</p>
              </div>
            </Reveal>
          ))}
        </ol>
      </div>
    </section>
  );
}
