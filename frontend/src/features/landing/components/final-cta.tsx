import { ArrowRight } from "lucide-react";
import Link from "next/link";

import { Reveal } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import { cn } from "@/lib/utils";

/**
 * Chamada final para ação. Painel em gradiente de marca (teal → verde) que
 * encerra a página com um único objetivo claro: começar a jornada.
 */
export function FinalCta() {
  return (
    <section className="py-20 sm:py-24">
      <div className={LANDING_CONTAINER_CLASS}>
        <Reveal className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-strong via-brand to-brand-green px-6 py-16 text-center shadow-xl sm:px-12 sm:py-20">
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.18),transparent_60%)]"
          />

          <div className="relative mx-auto flex max-w-2xl flex-col items-center gap-6">
            <h2 className="text-3xl font-bold tracking-tight text-balance text-white sm:text-4xl">
              Sua aprovação começa com o primeiro passo
            </h2>
            <p className="text-pretty text-white/85 sm:text-lg">
              Crie sua conta gratuita e transforme o processo seletivo do CEAP em uma
              jornada organizada, do cadastro ao resultado.
            </p>

            <Button
              size="lg"
              asChild
              className={cn(
                "group bg-white text-brand-strong hover:bg-white/90",
                "shadow-lg shadow-black/10",
              )}
            >
              <Link href="/cadastro">
                Criar minha conta
                <ArrowRight
                  className="size-4 transition-transform group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
            </Button>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
