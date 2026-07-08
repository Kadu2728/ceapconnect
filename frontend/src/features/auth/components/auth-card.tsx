"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

interface AuthCardProps {
  title: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
}

/**
 * Cartão compartilhado pelas telas de autenticação (login/cadastro),
 * garantindo cabeçalho e moldura visual consistentes entre os dois fluxos.
 *
 * Client Component isolado apenas pela animação de entrada (Framer Motion);
 * as páginas que o consomem seguem Server Components.
 */
export function AuthCard({ title, description, children, footer }: AuthCardProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: shouldReduceMotion ? 0 : 0.35, ease: "easeOut" }}
      className="rounded-2xl border bg-card px-6 py-8 shadow-sm sm:px-8"
    >
      <div className="mb-6 flex flex-col gap-1.5 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>

      {children}

      {footer ? (
        <div className="mt-6 text-center text-sm text-muted-foreground">{footer}</div>
      ) : null}
    </motion.div>
  );
}
