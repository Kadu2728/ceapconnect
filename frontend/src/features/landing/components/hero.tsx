"use client";

import { motion, useReducedMotion, type Variants } from "framer-motion";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { JourneyPreviewCard } from "@/features/landing/components/journey-preview";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import { cn } from "@/lib/utils";

function getContainerVariants(shouldReduceMotion: boolean): Variants {
  return {
    hidden: {},
    visible: {
      transition: { staggerChildren: shouldReduceMotion ? 0 : 0.1, delayChildren: 0.05 },
    },
  };
}

function getItemVariants(shouldReduceMotion: boolean): Variants {
  return {
    hidden: { opacity: 0, y: shouldReduceMotion ? 0 : 18 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: shouldReduceMotion ? 0 : 0.6, ease: [0.22, 1, 0.36, 1] },
    },
  };
}

const TRUST_POINTS = ["Grátis para candidatos", "Leva menos de 2 minutos"];

/**
 * Seção principal (above the fold) da Landing Page.
 *
 * Duas colunas no desktop: proposta de valor + CTAs à esquerda, prévia da
 * jornada à direita. Camada de fundo decorativa (glows de marca + grid sutil)
 * dá profundidade sem competir com o conteúdo. Entrada com stagger, respeitando
 * `prefers-reduced-motion`.
 */
export function Hero() {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getContainerVariants(shouldReduceMotion);
  const itemVariants = getItemVariants(shouldReduceMotion);

  return (
    <section className="relative overflow-hidden">
      {/* Fundo decorativo */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -top-32 -left-24 size-[32rem] rounded-full bg-brand/20 blur-3xl" />
        <div className="absolute top-10 right-0 size-[28rem] rounded-full bg-brand-green/15 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,var(--foreground)_1px,transparent_1px)] opacity-[0.04] [background-size:28px_28px]" />
      </div>

      <div
        className={cn(
          LANDING_CONTAINER_CLASS,
          "grid gap-12 py-16 sm:py-20 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-16 lg:py-28",
        )}
      >
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="flex flex-col items-start gap-6"
        >
          <motion.span
            variants={itemVariants}
            className="inline-flex items-center gap-2 rounded-full border border-brand/20 bg-brand/5 px-3 py-1.5 text-xs font-medium text-brand"
          >
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-brand-green opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-brand-green" />
            </span>
            40 anos · +10 mil jovens transformados
          </motion.span>

          <motion.h1
            variants={itemVariants}
            className="text-4xl font-bold tracking-tight text-balance sm:text-5xl lg:text-6xl"
          >
            Sua jornada até a{" "}
            <span className="bg-gradient-to-r from-brand to-brand-green bg-clip-text text-transparent">
              aprovação
            </span>{" "}
            no CEAP, do início ao fim.
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="max-w-xl text-lg text-pretty text-muted-foreground"
          >
            O CEAP Connect acompanha cada etapa do processo seletivo — prazos, missões e
            conquistas — em um só lugar. Menos ansiedade, mais progresso.
          </motion.p>

          <motion.div
            variants={itemVariants}
            className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:items-center"
          >
            <Button size="lg" asChild className="group">
              <Link href="/cadastro">
                Iniciar minha Jornada
                <ArrowRight
                  className="size-4 transition-transform group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
            </Button>

            <Button size="lg" variant="outline" asChild>
              <Link href="#jornada">Ver como funciona</Link>
            </Button>
          </motion.div>

          <motion.ul
            variants={itemVariants}
            className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted-foreground"
          >
            {TRUST_POINTS.map((point) => (
              <li key={point} className="flex items-center gap-1.5">
                <CheckCircle2 className="size-4 text-success" aria-hidden="true" />
                {point}
              </li>
            ))}
          </motion.ul>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            duration: shouldReduceMotion ? 0 : 0.7,
            delay: shouldReduceMotion ? 0 : 0.3,
            ease: [0.22, 1, 0.36, 1],
          }}
          className="flex justify-center lg:justify-end"
        >
          <JourneyPreviewCard />
        </motion.div>
      </div>
    </section>
  );
}
