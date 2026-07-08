"use client";

import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, X, XCircle, type LucideIcon } from "lucide-react";

import {
  useToastStore,
  type ToastVariant,
} from "@/components/feedback/toast/toast-store";
import { cn } from "@/lib/utils";

const VARIANT_CONTAINER_CLASS: Record<ToastVariant, string> = {
  success: "border-success/30 bg-success/10",
  error: "border-destructive/30 bg-destructive/10",
  info: "border-border bg-card",
};

const VARIANT_ICON: Record<ToastVariant, LucideIcon> = {
  success: CheckCircle2,
  error: XCircle,
  info: CheckCircle2,
};

const VARIANT_ICON_CLASS: Record<ToastVariant, string> = {
  success: "text-success",
  error: "text-destructive",
  info: "text-foreground",
};

/**
 * Viewport global de toasts (DESIGN_SYSTEM.md → "Toast"), montado uma única
 * vez em `AppProviders` para sobreviver a trocas de rota.
 *
 * Fixado no rodapé em mobile (alcance do polegar) e no canto superior
 * direito a partir do `sm`, convenção comum em produtos desktop
 * (Linear, Vercel).
 */
export function Toaster() {
  const toasts = useToastStore((state) => state.toasts);
  const dismiss = useToastStore((state) => state.dismiss);

  return (
    <div
      role="region"
      aria-label="Notificações"
      className="pointer-events-none fixed inset-x-4 bottom-4 z-50 flex flex-col gap-2 sm:inset-x-auto sm:top-4 sm:right-4 sm:bottom-auto sm:w-full sm:max-w-sm"
    >
      <AnimatePresence initial={false}>
        {toasts.map((item) => {
          const Icon = VARIANT_ICON[item.variant];

          return (
            <motion.div
              key={item.id}
              role="status"
              layout
              initial={{ opacity: 0, y: 16, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.15 } }}
              transition={{ duration: 0.2 }}
              className={cn(
                "pointer-events-auto flex items-start gap-3 rounded-xl border px-4 py-3 shadow-sm backdrop-blur",
                VARIANT_CONTAINER_CLASS[item.variant],
              )}
            >
              <Icon
                className={cn("mt-0.5 size-5 shrink-0", VARIANT_ICON_CLASS[item.variant])}
                aria-hidden="true"
              />

              <div className="flex-1 text-sm">
                <p className="font-medium text-foreground">{item.title}</p>
                {item.description ? (
                  <p className="mt-0.5 text-muted-foreground">{item.description}</p>
                ) : null}
              </div>

              <button
                type="button"
                onClick={() => dismiss(item.id)}
                aria-label="Fechar notificação"
                className="rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
              >
                <X className="size-4" aria-hidden="true" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
