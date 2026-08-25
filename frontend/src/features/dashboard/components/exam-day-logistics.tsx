"use client";

import { Check, MapPin } from "lucide-react";
import { useState } from "react";

import { DashboardCard } from "@/features/dashboard/components/dashboard-card";
import { cn } from "@/lib/utils";

interface ExamDayLogisticsProps {
  examLocation: string;
}

/**
 * Checklist do dia da prova (backlog "logística"): endereço + o que levar.
 *
 * Para o público do CEAP — jovens de baixa renda dependentes de transporte
 * público —, não saber onde é a prova ou esquecer um documento é uma
 * barreira real e concreta de perder a vaga, maior que qualquer elemento de
 * gamificação. Só aparece quando a prova está próxima (ver
 * `dashboard-content.tsx`), para não competir por atenção com o resto do
 * Dashboard fora dessa janela.
 *
 * O estado do checklist é só local (não persiste no backend, de propósito):
 * é uma conferência de última hora, feita uma vez, na manhã da prova — não
 * um progresso que precise sobreviver a um F5 ou a outro dispositivo.
 */
export function ExamDayLogistics({ examLocation }: ExamDayLogisticsProps) {
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  const toggleItem = (index: number) => {
    setCheckedItems((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(examLocation)}`;

  return (
    <DashboardCard className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Preparação para o dia da prova</h2>
      </div>

      <a
        href={mapsUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-start gap-3 rounded-xl border bg-muted/40 p-3 text-sm transition-colors hover:bg-muted"
      >
        <MapPin className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden="true" />
        <span>
          <span className="font-medium">{examLocation}</span>
          <span className="block text-xs text-muted-foreground">Ver no mapa</span>
        </span>
      </a>

      <ul className="flex flex-col gap-2">
        {_CHECKLIST_ITEMS.map((item, index) => {
          const checked = Boolean(checkedItems[index]);
          return (
            <li key={item}>
              <button
                type="button"
                onClick={() => toggleItem(index)}
                aria-pressed={checked}
                className="flex w-full items-center gap-3 rounded-lg px-1 py-1.5 text-left text-sm transition-colors hover:bg-muted/60"
              >
                <span
                  className={cn(
                    "flex size-5 shrink-0 items-center justify-center rounded-md border-2 transition-colors",
                    checked
                      ? "border-success bg-success text-success-foreground"
                      : "border-muted-foreground/40",
                  )}
                >
                  {checked ? <Check className="size-3.5" aria-hidden="true" /> : null}
                </span>
                <span className={cn(checked && "text-muted-foreground line-through")}>
                  {item}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </DashboardCard>
  );
}

const _CHECKLIST_ITEMS = [
  "Documento de identidade original com foto",
  "Comprovante de inscrição (ou CPF)",
  "Caneta esferográfica azul ou preta",
  "Chegar com pelo menos 30 minutos de antecedência",
  "Água e um lanche leve",
] as const;
