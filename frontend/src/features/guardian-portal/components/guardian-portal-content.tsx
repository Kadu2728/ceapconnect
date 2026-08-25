"use client";

import { CheckCircle2, MapPin } from "lucide-react";

import { Button } from "@/components/ui/button";
import { AuthCard } from "@/features/auth/components/auth-card";
import { formatFullDate } from "@/features/dashboard/utils/date";
import { useConfirmGuardianTraining } from "@/features/guardian-portal/hooks/use-confirm-guardian-training";
import { useGuardianPortal } from "@/features/guardian-portal/hooks/use-guardian-portal";

interface GuardianPortalContentProps {
  token: string;
}

/**
 * Portal do Responsável (item 5 do backlog) — acessado por link mágico
 * enviado por e-mail/WhatsApp pelo candidato, sem exigir conta/login. Único
 * lugar onde o próprio responsável (não o coordenador, não o candidato)
 * confirma presença na formação obrigatória.
 */
export function GuardianPortalContent({ token }: GuardianPortalContentProps) {
  const portalQuery = useGuardianPortal(token);
  const confirmMutation = useConfirmGuardianTraining(token);

  if (portalQuery.isPending) {
    return (
      <AuthCard title="Carregando…" description="Só um instante.">
        <div className="h-24 animate-pulse rounded-xl bg-muted" />
      </AuthCard>
    );
  }

  if (portalQuery.isError) {
    return (
      <AuthCard
        title="Link inválido"
        description="Este link de confirmação não é válido ou expirou. Peça para o candidato reenviar o convite."
      >
        {null}
      </AuthCard>
    );
  }

  const data = portalQuery.data;
  const alreadyConfirmed =
    Boolean(data.training_confirmed_at) || Boolean(data.training_attended_at);

  return (
    <AuthCard
      title={`Formação de ${data.candidate_first_name}`}
      description="Etapa obrigatória do processo seletivo do CEAP — sua presença é o que garante a vaga."
    >
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2 rounded-xl bg-muted/40 p-4 text-sm">
          <p className="font-medium">
            {data.training_date
              ? formatFullDate(data.training_date)
              : "Data ainda não definida"}
          </p>
          <p className="flex items-center gap-1.5 text-muted-foreground">
            <MapPin className="size-4 shrink-0" aria-hidden="true" />
            {data.training_location}
          </p>
        </div>

        {alreadyConfirmed ? (
          <div
            role="status"
            className="flex items-center gap-3 rounded-xl border border-success/30 bg-success/10 px-4 py-3 text-sm"
          >
            <CheckCircle2 className="size-5 shrink-0 text-success" aria-hidden="true" />
            <p>
              {data.training_attended_at
                ? "Presença confirmada — obrigado por participar!"
                : "Presença confirmada. Contamos com você lá!"}
            </p>
          </div>
        ) : (
          <Button
            size="lg"
            className="w-full"
            disabled={confirmMutation.isPending}
            onClick={() => confirmMutation.mutate()}
          >
            {confirmMutation.isPending ? "Confirmando…" : "Confirmar presença"}
          </Button>
        )}

        <p className="text-center text-xs text-muted-foreground">
          Dúvidas? Entre em contato com a secretaria do CEAP.
        </p>
      </div>
    </AuthCard>
  );
}
