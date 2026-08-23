"use client";

import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Mail, Phone, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useCreateGuardianIntervention } from "@/features/guardians/hooks/use-create-guardian-intervention";
import {
  useMarkTrainingAttended,
  useMarkTrainingConfirmed,
} from "@/features/guardians/hooks/use-mark-training";
import type {
  GuardianAtRiskItem,
  GuardianInterventionChannel,
  GuardianInterventionOutcome,
} from "@/features/guardians/types/guardian.types";
import { cn } from "@/lib/utils";

const CHANNEL_OPTIONS: { value: GuardianInterventionChannel; label: string }[] = [
  { value: "call", label: "Ligar" },
  { value: "whatsapp", label: "WhatsApp" },
  { value: "other", label: "Outro" },
];

const OUTCOME_OPTIONS: { value: GuardianInterventionOutcome; label: string }[] = [
  { value: "reached", label: "Consegui contato" },
  { value: "no_answer", label: "Não atendeu" },
  { value: "other", label: "Outro" },
];

interface GuardianDrawerProps {
  item: GuardianAtRiskItem | null;
  onClose: () => void;
}

/**
 * Gaveta do responsável (alvo duplo do Console de Intervenção). Opera direto
 * sobre o item já carregado na lista — não há endpoint de detalhe separado,
 * já que `GuardianAtRiskItem` já traz tudo que a gaveta precisa mostrar.
 */
export function GuardianDrawer({ item, onClose }: GuardianDrawerProps) {
  const isOpen = item !== null;

  return (
    <AnimatePresence>
      {isOpen && item ? (
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-label="Detalhe do responsável"
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
              <h2 className="font-semibold">Responsável</h2>
              <Button variant="ghost" size="icon" onClick={onClose} aria-label="Fechar">
                <X className="size-4" aria-hidden="true" />
              </Button>
            </div>

            <DrawerContent item={item} />
          </motion.aside>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}

function DrawerContent({ item }: { item: GuardianAtRiskItem }) {
  return (
    <div className="flex flex-1 flex-col gap-6 p-5">
      <div>
        <h3 className="font-semibold">{item.candidate_name}</h3>
        <p className="text-sm text-muted-foreground">{item.candidate_email}</p>
        {item.cohort_name ? (
          <p className="mt-0.5 text-xs text-muted-foreground">{item.cohort_name}</p>
        ) : null}
      </div>

      <span className="w-fit rounded-full bg-warning/10 px-3 py-1 text-xs font-semibold text-warning">
        {item.reason}
      </span>

      {item.guardian_id === null ? (
        <p className="rounded-lg border border-dashed p-3 text-sm text-muted-foreground">
          Nenhum responsável cadastrado ainda. Oriente o candidato a preencher o contato
          do responsável na tela de Perfil — sem isso não é possível registrar um contato
          aqui.
        </p>
      ) : (
        <GuardianActions item={item} guardianId={item.guardian_id} />
      )}
    </div>
  );
}

function GuardianActions({
  item,
  guardianId,
}: {
  item: GuardianAtRiskItem;
  guardianId: string;
}) {
  const markConfirmed = useMarkTrainingConfirmed();
  const markAttended = useMarkTrainingAttended();

  return (
    <>
      <section className="flex flex-col gap-2 rounded-lg border p-3">
        <h4 className="text-sm font-semibold">Contato do responsável</h4>
        {item.guardian_name ? <p className="text-sm">{item.guardian_name}</p> : null}
        <div className="flex flex-col gap-1 text-sm text-muted-foreground">
          {item.guardian_phone ? (
            <span className="flex items-center gap-1.5">
              <Phone className="size-3.5" aria-hidden="true" /> {item.guardian_phone}
            </span>
          ) : null}
          {item.guardian_email ? (
            <span className="flex items-center gap-1.5">
              <Mail className="size-3.5" aria-hidden="true" /> {item.guardian_email}
            </span>
          ) : null}
          {!item.guardian_phone && !item.guardian_email ? (
            <span>Sem telefone ou e-mail cadastrado.</span>
          ) : null}
        </div>
      </section>

      <section className="flex flex-col gap-2">
        <h4 className="text-sm font-semibold">Formação obrigatória</h4>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={markConfirmed.isPending || Boolean(item.training_confirmed_at)}
            onClick={() => markConfirmed.mutate(guardianId)}
          >
            {item.training_confirmed_at ? "Presença confirmada" : "Marcar confirmação"}
          </Button>
          <Button
            type="button"
            size="sm"
            disabled={markAttended.isPending}
            onClick={() => markAttended.mutate(guardianId)}
          >
            <CheckCircle2 className="size-4" aria-hidden="true" />
            Marcar presença na formação
          </Button>
        </div>
      </section>

      <NewGuardianInterventionForm guardianId={guardianId} />
    </>
  );
}

function NewGuardianInterventionForm({ guardianId }: { guardianId: string }) {
  const [channel, setChannel] = useState<GuardianInterventionChannel>("whatsapp");
  const [outcome, setOutcome] = useState<GuardianInterventionOutcome>("reached");
  const [notes, setNotes] = useState("");
  const mutation = useCreateGuardianIntervention();

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    mutation.mutate(
      { guardian_id: guardianId, channel, outcome, notes: notes.trim() || undefined },
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
          <Label htmlFor="guardian-intervention-notes">Notas (opcional)</Label>
          <textarea
            id="guardian-intervention-notes"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            maxLength={1000}
            rows={2}
            placeholder="O que foi conversado, próximos passos..."
            className="flex w-full resize-y rounded-md border border-input bg-transparent px-3 py-1.5 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
          />
        </div>

        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Registrando…" : "Registrar contato"}
        </Button>
      </form>
    </section>
  );
}

function ToggleButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
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
      {label}
    </button>
  );
}
