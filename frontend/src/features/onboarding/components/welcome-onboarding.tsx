"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  ArrowRight,
  Award,
  CalendarDays,
  Route,
  Target,
  type LucideIcon,
} from "lucide-react";

import { CeapMark } from "@/components/brand/ceap-logo";
import { Button } from "@/components/ui/button";

interface OnboardingStep {
  icon: LucideIcon;
  title: string;
  text: string;
}

const STEPS: OnboardingStep[] = [
  { icon: Route, title: "Jornada", text: "Veja onde você está e o próximo passo." },
  { icon: Target, title: "Missões", text: "Complete ações e ganhe XP." },
  { icon: Award, title: "Conquistas", text: "Desbloqueie marcos da sua evolução." },
  { icon: CalendarDays, title: "Eventos", text: "Participe e prepare-se para a prova." },
];

interface WelcomeOnboardingProps {
  name: string;
  onFinish: () => void;
  isFinishing: boolean;
}

/**
 * Tela de boas-vindas do primeiro login (USER_FLOW.md → "Primeiro Login").
 * Overlay modal que apresenta os pilares do produto e leva o candidato ao
 * Dashboard. Aparece uma única vez (controlado por `onboarded` no backend).
 */
export function WelcomeOnboarding({
  name,
  onFinish,
  isFinishing,
}: WelcomeOnboardingProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="welcome-title"
      className="fixed inset-0 z-[60] flex items-center justify-center bg-foreground/40 p-4 backdrop-blur-sm"
    >
      <motion.div
        initial={{
          opacity: 0,
          scale: shouldReduceMotion ? 1 : 0.96,
          y: shouldReduceMotion ? 0 : 12,
        }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: shouldReduceMotion ? 0 : 0.3, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md overflow-hidden rounded-3xl border border-border/70 bg-card shadow-2xl"
      >
        <div className="bg-gradient-to-br from-brand to-brand-green px-6 py-8 text-center text-brand-foreground">
          <span className="mx-auto flex size-14 items-center justify-center rounded-2xl bg-white/15">
            <CeapMark className="size-9" />
          </span>
          <h2 id="welcome-title" className="mt-4 text-2xl font-bold">
            Bem-vindo(a), {name}!
          </h2>
          <p className="mt-1 text-sm text-brand-foreground/85">
            Sua jornada no CEAP começa agora. Veja o que você encontra por aqui:
          </p>
        </div>

        <ul className="grid grid-cols-2 gap-3 p-6">
          {STEPS.map((step) => {
            const Icon = step.icon;
            return (
              <li key={step.title} className="rounded-xl border border-border/60 p-3">
                <span className="flex size-9 items-center justify-center rounded-lg bg-brand/10 text-brand">
                  <Icon className="size-5" aria-hidden="true" />
                </span>
                <h3 className="mt-2 text-sm font-semibold text-foreground">
                  {step.title}
                </h3>
                <p className="mt-0.5 text-xs text-muted-foreground">{step.text}</p>
              </li>
            );
          })}
        </ul>

        <div className="px-6 pb-6">
          <Button
            size="lg"
            onClick={onFinish}
            disabled={isFinishing}
            className="group w-full"
          >
            {isFinishing ? "Vamos lá…" : "Começar minha jornada"}
            <ArrowRight
              className="size-4 transition-transform group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
