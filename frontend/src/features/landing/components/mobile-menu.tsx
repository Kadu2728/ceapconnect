"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { LANDING_CONTAINER_CLASS } from "@/features/landing/utils/layout";
import { cn } from "@/lib/utils";

interface MobileMenuLink {
  href: string;
  label: string;
}

interface MobileMenuProps {
  links: MobileMenuLink[];
}

/**
 * Menu de navegação para telas pequenas (&lt; md). Um único botão de toque
 * abre um painel com as âncoras de seção e os atalhos de conta — garantindo
 * que toda a navegação da Landing seja alcançável no celular (público
 * majoritariamente mobile). Fecha ao tocar em um link, no backdrop ou com Esc,
 * e respeita `prefers-reduced-motion`.
 */
export function MobileMenu({ links }: MobileMenuProps) {
  const [open, setOpen] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    if (!open) return;

    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open]);

  return (
    <div className="md:hidden">
      <Button
        variant="outline"
        size="icon"
        className="size-9"
        aria-label={open ? "Fechar menu" : "Abrir menu"}
        aria-expanded={open}
        aria-controls="mobile-menu-panel"
        onClick={() => setOpen((value) => !value)}
      >
        {open ? <X className="size-4" /> : <Menu className="size-4" />}
      </Button>

      <AnimatePresence>
        {open ? (
          <>
            <motion.button
              type="button"
              aria-hidden="true"
              tabIndex={-1}
              className="fixed inset-x-0 top-16 bottom-0 z-30 bg-foreground/20 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.2 }}
              onClick={() => setOpen(false)}
            />

            <motion.nav
              id="mobile-menu-panel"
              aria-label="Menu principal"
              className="absolute inset-x-0 top-16 z-40 border-b border-border/60 bg-background/95 backdrop-blur-xl"
              initial={{ opacity: 0, y: shouldReduceMotion ? 0 : -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: shouldReduceMotion ? 0 : -8 }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.2, ease: "easeOut" }}
            >
              <div className={cn(LANDING_CONTAINER_CLASS, "flex flex-col gap-1 py-4")}>
                {links.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setOpen(false)}
                    className="rounded-lg px-3 py-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                  >
                    {link.label}
                  </Link>
                ))}

                <div className="mt-2 flex flex-col gap-2 border-t border-border/60 pt-3">
                  <Button variant="outline" asChild>
                    <Link href="/login" onClick={() => setOpen(false)}>
                      Entrar
                    </Link>
                  </Button>
                  <Button asChild>
                    <Link href="/cadastro" onClick={() => setOpen(false)}>
                      Criar conta
                    </Link>
                  </Button>
                </div>
              </div>
            </motion.nav>
          </>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
