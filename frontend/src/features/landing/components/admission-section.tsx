"use client";

import { motion, useReducedMotion } from "framer-motion";

import { SectionHeading } from "@/features/landing/components/section-heading";
import { SELECTION_STEPS } from "@/features/landing/data/admissions";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

/**
 * Processo seletivo do CEAP em três etapas (inscrição, prova e entrevista),
 * apresentadas como passos numerados e sequenciais. Reforça que a seleção é
 * 100% gratuita.
 */
export function AdmissionSection() {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  return (
    <section
      id="ingresso"
      className="scroll-mt-20 border-t border-border/60 bg-muted/20 py-20 sm:py-24"
    >
      <div className={LANDING_CONTAINER_CLASS}>
        <SectionHeading
          eyebrow="Processo seletivo"
          title="Três passos até a sua vaga"
          description="A seleção do CEAP é totalmente gratuita. Do cadastro à entrevista, o CEAP Connect acompanha você em cada etapa."
        />

        <motion.ol
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={containerVariants}
          className="mt-14 grid grid-cols-1 gap-4 md:grid-cols-3"
        >
          {SELECTION_STEPS.map((step, index) => {
            const Icon = step.icon;
            return (
              <motion.li key={step.title} variants={itemVariants}>
                <div className="relative flex h-full flex-col gap-4 rounded-2xl border border-border/70 bg-card p-6 transition-all duration-300 hover:-translate-y-1 hover:border-brand/40 hover:shadow-lg">
                  <div className="flex items-center justify-between">
                    <span className="flex size-11 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-2 text-brand-foreground">
                      <Icon className="size-5" aria-hidden="true" />
                    </span>
                    <span className="text-3xl font-bold tabular-nums text-muted-foreground/25">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-semibold text-foreground">{step.title}</h3>
                    <p className="mt-1.5 text-sm text-muted-foreground">
                      {step.description}
                    </p>
                  </div>
                </div>
              </motion.li>
            );
          })}
        </motion.ol>
      </div>
    </section>
  );
}
