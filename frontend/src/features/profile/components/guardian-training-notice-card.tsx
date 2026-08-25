"use client";

import { CheckCircle2, Mail, MapPin, MessageCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { formatFullDate } from "@/features/dashboard/utils/date";
import { useNotifyGuardianTrainingEmail } from "@/features/profile/hooks/use-notify-guardian-training-email";
import type { Profile } from "@/features/profile/types/profile.types";
import { buildGuardianTrainingWhatsAppLink } from "@/features/profile/utils/guardian-training-whatsapp";

interface GuardianTrainingNoticeCardProps {
  profile: Profile;
}

/**
 * Aviso ao responsável sobre a formação obrigatória (item 5 do backlog).
 * Diferente do card da entrevista: esta etapa é autoconfirmável — o próprio
 * responsável confirma presença pelo link (`/responsavel/{token}`), sem
 * precisar de conta. O candidato só dá o empurrão inicial (avisar), o resto
 * acontece direto entre o responsável e o CEAP.
 */
export function GuardianTrainingNoticeCard({ profile }: GuardianTrainingNoticeCardProps) {
  const notifyMutation = useNotifyGuardianTrainingEmail();
  const hasGuardianContact = Boolean(profile.guardian_phone || profile.guardian_email);
  const whatsappLink = buildGuardianTrainingWhatsAppLink(profile.name, profile);
  const alreadyConfirmed =
    Boolean(profile.guardian_training_confirmed_at) ||
    Boolean(profile.guardian_training_attended_at);

  return (
    <Card className="gap-4">
      <div className="px-6">
        <h3 className="font-semibold">Formação obrigatória do responsável</h3>
        <p className="text-sm text-muted-foreground">
          Etapa obrigatória do processo seletivo — sem ela, a vaga é perdida.
        </p>
      </div>

      <div className="flex flex-col gap-2 px-6 text-sm">
        <p className="font-medium">
          {profile.guardian_training_date
            ? formatFullDate(profile.guardian_training_date)
            : "Data ainda não definida"}
        </p>
        <p className="flex items-center gap-1.5 text-muted-foreground">
          <MapPin className="size-4 shrink-0" aria-hidden="true" />
          {profile.interview_location}
        </p>
      </div>

      {alreadyConfirmed ? (
        <p className="mx-6 flex items-center gap-2 rounded-lg bg-success/10 px-4 py-3 text-sm text-success">
          <CheckCircle2 className="size-4 shrink-0" aria-hidden="true" />
          Seu responsável já confirmou presença.
        </p>
      ) : hasGuardianContact ? (
        <div className="flex flex-col gap-2 px-6 sm:flex-row">
          <Button asChild variant="outline" className="flex-1">
            <a href={whatsappLink} target="_blank" rel="noopener noreferrer">
              <MessageCircle className="size-4" aria-hidden="true" />
              Enviar por WhatsApp
            </a>
          </Button>
          <Button
            className="flex-1"
            disabled={!profile.guardian_email || notifyMutation.isPending}
            onClick={() => notifyMutation.mutate()}
          >
            <Mail className="size-4" aria-hidden="true" />
            {notifyMutation.isPending
              ? "Enviando…"
              : profile.guardian_training_notified_at
                ? `Reenviar e-mail (enviado em ${formatFullDate(profile.guardian_training_notified_at)})`
                : "Enviar por e-mail"}
          </Button>
        </div>
      ) : (
        <p className="mx-6 rounded-lg bg-accent/40 px-4 py-3 text-sm text-muted-foreground">
          Cadastre o telefone ou e-mail do seu responsável abaixo para poder avisá-lo.
        </p>
      )}
    </Card>
  );
}
