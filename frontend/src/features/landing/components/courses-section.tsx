"use client";

import { motion, useReducedMotion } from "framer-motion";

import { SectionHeading } from "@/features/landing/components/section-heading";
import { COURSES } from "@/features/landing/data/courses";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

/**
 * Vitrine dos cursos técnicos gratuitos do CEAP. Dá concretude ao processo
 * seletivo — o candidato vê exatamente para onde a jornada leva. Grid
 * responsivo (1 → 2 → 4 colunas) com stagger de entrada.
 */
export function CoursesSection() {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  return (
    <section id="cursos" className="scroll-mt-20 py-20 sm:py-24">
      <div className={LANDING_CONTAINER_CLASS}>
        <SectionHeading
          eyebrow="Cursos técnicos gratuitos"
          title="Quatro caminhos para o seu futuro"
          description="Formação técnica de verdade, sem custo nenhum. Escolha o curso que combina com você e comece a se preparar desde já."
        />

        <motion.ul
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={containerVariants}
          className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          {COURSES.map((course) => {
            const Icon = course.icon;
            return (
              <motion.li key={course.name} variants={itemVariants}>
                <div className="group flex h-full flex-col gap-4 rounded-2xl border border-border/70 bg-card p-6 transition-all duration-300 hover:-translate-y-1 hover:border-brand/40 hover:shadow-lg">
                  <span className="flex size-11 items-center justify-center rounded-xl bg-brand/10 text-brand transition-colors duration-300 group-hover:bg-brand group-hover:text-brand-foreground">
                    <Icon className="size-5" aria-hidden="true" />
                  </span>
                  <div>
                    <h3 className="font-semibold text-foreground">{course.name}</h3>
                    <p className="mt-1.5 text-sm text-muted-foreground">
                      {course.description}
                    </p>
                  </div>
                </div>
              </motion.li>
            );
          })}
        </motion.ul>
      </div>
    </section>
  );
}
