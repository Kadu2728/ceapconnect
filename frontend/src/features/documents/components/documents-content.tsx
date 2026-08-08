"use client";

import { motion, useReducedMotion } from "framer-motion";
import { CheckCircle2, FolderCheck } from "lucide-react";

import { Card } from "@/components/ui/card";
import { DocumentCard } from "@/features/documents/components/document-card";
import type { DocumentChecklist } from "@/features/documents/types/document.types";
import {
  getStaggerContainerVariants,
  getStaggerItemVariants,
} from "@/lib/motion-variants";

interface DocumentsContentProps {
  data: DocumentChecklist;
}

/**
 * Composição da tela de Documentos: resumo de progresso + checklist. Estado
 * de conclusão comemorativo — completar o checklist é literalmente o passo
 * que a predição de evasão (EPIC 14) identificou como o mais travado.
 */
export function DocumentsContent({ data }: DocumentsContentProps) {
  const shouldReduceMotion = Boolean(useReducedMotion());
  const containerVariants = getStaggerContainerVariants(shouldReduceMotion);
  const itemVariants = getStaggerItemVariants(shouldReduceMotion);

  const percentage =
    data.total_required > 0
      ? Math.round((data.total_uploaded / data.total_required) * 100)
      : 0;

  return (
    <div className="flex flex-col gap-6">
      <Card className="gap-4">
        <div className="flex items-center justify-between px-6">
          <div>
            <p className="text-sm text-muted-foreground">Documentos enviados</p>
            <p className="text-2xl font-bold tracking-tight">
              {data.total_uploaded}
              <span className="text-lg font-medium text-muted-foreground">
                /{data.total_required}
              </span>
            </p>
          </div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-accent px-3.5 py-1.5 text-sm font-semibold text-accent-foreground">
            <FolderCheck className="size-4" aria-hidden="true" />
            {percentage}%
          </span>
        </div>

        <div className="px-6">
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-gradient-to-r from-brand to-brand-green transition-[width] duration-500"
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>

        {data.all_complete ? (
          <div className="mx-6 flex items-center gap-2 rounded-lg bg-success/10 px-4 py-3 text-sm font-medium text-success">
            <CheckCircle2 className="size-4 shrink-0" aria-hidden="true" />
            Checklist completo! Sua documentação está pronta para a próxima etapa.
          </div>
        ) : null}
      </Card>

      <motion.ul
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="flex flex-col gap-4"
      >
        {data.documents.map((document) => (
          <motion.li key={document.document_type} variants={itemVariants}>
            <DocumentCard document={document} />
          </motion.li>
        ))}
      </motion.ul>
    </div>
  );
}
