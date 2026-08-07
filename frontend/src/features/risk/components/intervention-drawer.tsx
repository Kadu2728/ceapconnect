"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  Check,
  CheckCheck,
  Clock,
  FileUp,
  LogIn,
  Phone,
  Target,
  TrendingDown,
  TrendingUp,
  X,
  type LucideIcon,
} from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RiskBadge } from "@/features/risk/components/risk-badge";
import { RiskExplanationDetailed } from "@/features/risk/components/risk-explanation";
import { useCandidateRisk } from "@/features/risk/hooks/use-candidate-risk";
import { useCreateIntervention } from "@/features/risk/hooks/use-create-intervention";
import type {
  InterventionChannel,
  InterventionOutcome,
} from "@/features/risk/types/risk.types";
import { cn } from "@/lib/utils";

const WHEN_FORMATTER = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

const ACTIVITY_ICON_MAP: Record<string, LucideIcon> = {
  login: LogIn,
  step_viewed: Clock,
  step_completed: CheckCheck,
  mission_started: Target,
  mission_completed: Check,
  mission_abandoned: X,
  document_uploaded: FileUp,
};

const CHANNEL_OPTIONS: { value: InterventionChannel; label: string }[] = [
  { value: "call", label: "Ligar" },
  { value: "whatsapp", label: "WhatsApp" },
  { value: "other", label: "Outro" },
];

const OUTCOME_OPTIONS: { value: InterventionOutcome; label: string }[] = [
  { value: "reached", label: "Consegui contato" },
  { value: "no_answer", label: "Não atendeu" },
  { value: "other", label: "Outro" },
];

interface InterventionDrawerProps {
  candidateProfileId: string | null;
  onClose: () => void;
}

/**
 * Gaveta lateral do candidato: score + fatores detalhados, timeline de
 * atividade recente, histórico de intervenções (com o resultado medido 7 dias
 * depois) e o formulário para registrar um novo contato. Abre por cima da
 * fila — nunca navega para outra página, para o coordenador voltar rápido.
 */
export function InterventionDrawer({
  candidateProfileId,
  onClose,
}: InterventionDrawerProps) {
  const isOpen = candidateProfileId !== null;
  const { data, isPending, isSuccess } = useCandidateRisk(candidateProfileId);

  return (
    <AnimatePresence>
      {isOpen ? (
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-label="Detalhe de risco do candidato"
          className="fixed inset-0 z-50 flex justify-end"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <button
            type="button"
            aria-label="Fechar"
            onClick={onClose}
            className="absolute inset-0 cursor-default bg-black/50 backdrop-blur-sm"
          />

          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 32 }}
            className="relative z-10 flex h-full w-full max-w-md flex-col overflow-y-auto border-l bg-card shadow-xl"
          >
            <div className="flex items-center justify-between border-b px-5 py-4">
              <h2 className="font-semibold">Detalhe do candidato</h2>
              <Button variant="ghost" size="icon" onClick={onClose} aria-label="Fechar">
                <X className="size-4" aria-hidden="true" />
              </Button>
            </div>

            {isPending ? (
              <div className="flex-1 animate-pulse space-y-4 p-5">
                <div className="h-6 w-2/3 rounded bg-muted" />
                <div className="h-4 w-1/2 rounded bg-muted" />
                <div className="h-24 rounded bg-muted" />
              </div>
            ) : isSuccess && data ? (
              <DrawerContent
                candidateProfileId={candidateProfileId as string}
                data={data}
              />
            ) : (
              <p className="p-5 text-sm text-muted-foreground">
                Não foi possível carregar este candidato.
              </p>
            )}
          </motion.aside>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}

function DrawerContent({
  candidateProfileId,
  data,
}: {
  candidateProfileId: string;
  data: NonNullable<ReturnType<typeof useCandidateRisk>["data"]>;
}) {
  return (
    <div className="flex flex-1 flex-col gap-6 p-5">
      <div>
        <h3 className="font-semibold">{data.candidate_name}</h3>
        <p className="text-sm text-muted-foreground">{data.candidate_email}</p>
        {data.cohort_name ? (
          <p className="mt-0.5 text-xs text-muted-foreground">{data.cohort_name}</p>
        ) : null}
      </div>

      {data.score !== null && data.tier !== null ? (
        <RiskBadge score={data.score} tier={data.tier} className="w-fit" />
      ) : (
        <p className="text-sm text-muted-foreground">Score ainda não calculado.</p>
      )}

      <section className="flex flex-col gap-2">
        <h4 className="text-sm font-semibold">Por que este score</h4>
        <RiskExplanationDetailed factors={data.factors} />
      </section>

      <section className="flex flex-col gap-2">
        <h4 className="text-sm font-semibold">Atividade recente</h4>
        {data.recent_activity.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nenhuma atividade registrada.</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {data.recent_activity.slice(0, 8).map((event, index) => {
              const Icon = ACTIVITY_ICON_MAP[event.name] ?? Clock;
              return (
                <li
                  key={`${event.name}-${event.occurred_at}-${index}`}
                  className="flex items-center gap-2.5 text-sm"
                >
                  <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                    <Icon className="size-3.5" aria-hidden="true" />
                  </span>
                  <span className="min-w-0 flex-1 truncate text-muted-foreground">
                    {event.name}
                  </span>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {WHEN_FORMATTER.format(new Date(event.occurred_at))}
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section className="flex flex-col gap-2">
        <h4 className="text-sm font-semibold">Histórico de intervenções</h4>
        {data.interventions.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Nenhuma intervenção registrada ainda.
          </p>
        ) : (
          <ul className="flex flex-col gap-3">
            {data.interventions.map((intervention) => (
              <li key={intervention.id} className="rounded-lg border p-3 text-sm">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">
                    {CHANNEL_OPTIONS.find((c) => c.value === intervention.channel)?.label}
                    {" · "}
                    {OUTCOME_OPTIONS.find((o) => o.value === intervention.outcome)?.label}
                  </span>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {WHEN_FORMATTER.format(new Date(intervention.created_at))}
                  </span>
                </div>
                {intervention.notes ? (
                  <p className="mt-1 text-muted-foreground">{intervention.notes}</p>
                ) : null}
                <div className="mt-2 flex items-center gap-1.5 text-xs">
                  {intervention.score_delta === null ? (
                    <span className="text-muted-foreground">
                      Resultado medido em 7 dias (aguardando)
                    </span>
                  ) : intervention.score_delta < 0 ? (
                    <span className="flex items-center gap-1 font-medium text-success">
                      <TrendingDown className="size-3.5" aria-hidden="true" />
                      Risco caiu {Math.abs(intervention.score_delta)} pontos
                    </span>
                  ) : intervention.score_delta > 0 ? (
                    <span className="flex items-center gap-1 font-medium text-destructive">
                      <TrendingUp className="size-3.5" aria-hidden="true" />
                      Risco subiu {intervention.score_delta} pontos
                    </span>
                  ) : (
                    <span className="text-muted-foreground">Score não mudou</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <NewInterventionForm
        candidateProfileId={candidateProfileId}
        disabled={data.score === null}
      />
    </div>
  );
}

function NewInterventionForm({
  candidateProfileId,
  disabled,
}: {
  candidateProfileId: string;
  disabled: boolean;
}) {
  const [channel, setChannel] = useState<InterventionChannel>("whatsapp");
  const [outcome, setOutcome] = useState<InterventionOutcome>("reached");
  const [notes, setNotes] = useState("");
  const mutation = useCreateIntervention();

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    mutation.mutate(
      {
        candidate_profile_id: candidateProfileId,
        channel,
        outcome,
        notes: notes.trim() || undefined,
      },
      { onSuccess: () => setNotes("") },
    );
  }

  return (
    <section className="mt-auto flex flex-col gap-3 border-t pt-4">
      <h4 className="text-sm font-semibold">Registrar contato</h4>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div className="flex flex-col gap-1.5">
          <Label>Canal</Label>
          <div className="flex gap-2">
            {CHANNEL_OPTIONS.map((option) => (
              <ToggleButton
                key={option.value}
                active={channel === option.value}
                label={option.label}
                icon={option.value === "call" ? Phone : undefined}
                onClick={() => setChannel(option.value)}
              />
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label>Resultado</Label>
          <div className="flex flex-wrap gap-2">
            {OUTCOME_OPTIONS.map((option) => (
              <ToggleButton
                key={option.value}
                active={outcome === option.value}
                label={option.label}
                onClick={() => setOutcome(option.value)}
              />
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="intervention-notes">Notas (opcional)</Label>
          <textarea
            id="intervention-notes"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            maxLength={1000}
            rows={2}
            placeholder="O que foi conversado, próximos passos..."
            className="flex w-full resize-y rounded-md border border-input bg-transparent px-3 py-1.5 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
          />
        </div>

        <Button type="submit" disabled={disabled || mutation.isPending}>
          {mutation.isPending ? "Registrando…" : "Registrar intervenção"}
        </Button>
        {disabled ? (
          <p className="text-xs text-muted-foreground">
            Este candidato ainda não tem score calculado — aguarde o próximo recálculo.
          </p>
        ) : null}
      </form>
    </section>
  );
}

function ToggleButton({
  active,
  label,
  icon: Icon,
  onClick,
}: {
  active: boolean;
  label: string;
  icon?: LucideIcon;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm font-medium transition-colors",
        active
          ? "border-brand bg-brand/10 text-brand"
          : "border-input text-muted-foreground hover:bg-accent/50",
      )}
    >
      {Icon ? <Icon className="size-3.5" aria-hidden="true" /> : null}
      {label}
    </button>
  );
}
