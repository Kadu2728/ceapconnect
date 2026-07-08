"use client";

import { motion, useReducedMotion } from "framer-motion";

import { PillarCard } from "@/features/landing/components/pillar-card";
import { SectionHeading } from "@/features/landing/components/section-heading";
import { PILLARS } from "@/features/landing/data/pillars";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

/**
 * Seção "Como funciona": os cinco pilares do produto. Entrada revelada ao rolar
 * (`whileInView`, uma vez), com stagger sutil — reforça progressão sem repetir a
 * animação a cada scroll.
 */
export function Pillars() {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  return (
    <section id="jornada" className="scroll-mt-20 py-20 sm:py-24">
      <div className={LANDING_CONTAINER_CLASS}>
        <SectionHeading
          eyebrow="Como funciona"
          title="Uma jornada, cinco pilares"
          description="Da inscrição ao dia da prova, cada etapa é acompanhada com clareza — sem gamificação infantil, só progresso real."
        />

        <motion.ul
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={containerVariants}
          className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5"
        >
          {PILLARS.map((pillar) => (
            <motion.li key={pillar.title} variants={itemVariants}>
              <PillarCard pillar={pillar} />
            </motion.li>
          ))}
        </motion.ul>
      </div>
    </section>
  );
}
