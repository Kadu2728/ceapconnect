"use client";

import { Check, Eye, FileText, RotateCcw, Trash2, Upload } from "lucide-react";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useDeleteDocument } from "@/features/documents/hooks/use-delete-document";
import { useUploadDocument } from "@/features/documents/hooks/use-upload-document";
import { fetchDocumentFileUrl } from "@/features/documents/services/document.service";
import type { DocumentItem } from "@/features/documents/types/document.types";
import { cn } from "@/lib/utils";

const ACCEPTED_TYPES = "image/jpeg,image/png,application/pdf";

function formatFileSize(bytes: number): string {
  return bytes < 1024 * 1024
    ? `${Math.round(bytes / 1024)} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

interface DocumentCardProps {
  document: DocumentItem;
}

/**
 * Card de um item do checklist de documentos. Não enviado: input de arquivo
 * escondido, disparado por um botão claro (`upload-flow`). Enviado: estado
 * calmo (nome + data), com "Ver" (abre o arquivo) e "Substituir"/"Remover".
 */
export function DocumentCard({ document }: DocumentCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const uploadMutation = useUploadDocument();
  const deleteMutation = useDeleteDocument();

  function handleFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = ""; // permite selecionar o mesmo arquivo de novo depois
    if (!file) return;
    uploadMutation.mutate({ documentType: document.document_type, file });
  }

  async function handleView() {
    setIsPreviewLoading(true);
    try {
      const url = await fetchDocumentFileUrl(document.document_type);
      window.open(url, "_blank", "noopener,noreferrer");
    } finally {
      setIsPreviewLoading(false);
    }
  }

  const isBusy = uploadMutation.isPending || deleteMutation.isPending;

  return (
    <Card
      className={cn(
        "gap-4 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md",
        document.uploaded && "border-success/30 bg-success/[0.03]",
      )}
    >
      <div className="flex items-start gap-4 px-6">
        <span
          className={cn(
            "flex size-11 shrink-0 items-center justify-center rounded-xl",
            document.uploaded ? "bg-success/15 text-success" : "bg-brand/10 text-brand",
          )}
        >
          {document.uploaded ? (
            <Check className="size-5" aria-hidden="true" />
          ) : (
            <FileText className="size-5" aria-hidden="true" />
          )}
        </span>

        <div className="min-w-0 flex-1">
          <h3 className="font-semibold">{document.label}</h3>
          <p className="mt-0.5 text-sm text-muted-foreground">{document.description}</p>

          {document.uploaded && document.uploaded_at ? (
            <p className="mt-2 text-xs text-muted-foreground">
              {document.file_name}
              {document.file_size ? ` · ${formatFileSize(document.file_size)}` : ""} ·
              enviado em {formatDate(document.uploaded_at)}
            </p>
          ) : null}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 px-6">
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          onChange={handleFileSelected}
          className="hidden"
          aria-label={`Selecionar arquivo para ${document.label}`}
        />

        {document.uploaded ? (
          <>
            <Button
              size="sm"
              variant="outline"
              onClick={handleView}
              disabled={isPreviewLoading}
            >
              <Eye className="size-4" aria-hidden="true" />
              {isPreviewLoading ? "Abrindo…" : "Ver"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => inputRef.current?.click()}
              disabled={isBusy}
            >
              <RotateCcw className="size-4" aria-hidden="true" />
              Substituir
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => deleteMutation.mutate(document.document_type)}
              disabled={isBusy}
              className="text-destructive hover:bg-destructive/10 hover:text-destructive"
            >
              <Trash2 className="size-4" aria-hidden="true" />
              Remover
            </Button>
          </>
        ) : (
          <Button size="sm" onClick={() => inputRef.current?.click()} disabled={isBusy}>
            <Upload className="size-4" aria-hidden="true" />
            {uploadMutation.isPending ? "Enviando…" : "Enviar arquivo"}
          </Button>
        )}
      </div>
    </Card>
  );
}
