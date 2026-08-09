"use client";

import { Mail, MapPin, MessageCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { formatFullDate } from "@/features/dashboard/utils/date";
import { useNotifyGuardianEmail } from "@/features/profile/hooks/use-notify-guardian-email";
import type { Profile } from "@/features/profile/types/profile.types";
import { buildGuardianWhatsAppLink } from "@/features/profile/utils/guardian-whatsapp";

interface GuardianNoticeCardProps {
  profile: Profile;
}

/**
 * Aviso ao responsável sobre a entrevista (EPIC 17). A entrevista é uma
 * etapa obrigatória do processo seletivo do CEAP e o responsável não tem
 * conta no app — este card dá ao candidato duas ações reais para avisá-lo:
 * e-mail (confirmado pelo servidor) e WhatsApp (link direto, sempre
 * disponível, sem depender de nenhuma integração paga).
 */
export function GuardianNoticeCard({ profile }: GuardianNoticeCardProps) {
  const notifyMutation = useNotifyGuardianEmail();
  const hasGuardianContact = Boolean(profile.guardian_phone || profile.guardian_email);
  const whatsappLink = buildGuardianWhatsAppLink(profile.name, profile);

  return (
    <Card className="gap-4">
      <div className="px-6">
        <h3 className="font-semibold">Entrevista com o responsável</h3>
        <p className="text-sm text-muted-foreground">
          Etapa obrigatória do processo seletivo — avise quem vai te acompanhar.
        </p>
      </div>

      <div className="flex flex-col gap-2 px-6 text-sm">
        <p className="font-medium">
          {profile.interview_date
            ? formatFullDate(profile.interview_date)
            : "Data ainda não definida"}
        </p>
        <p className="flex items-center gap-1.5 text-muted-foreground">
          <MapPin className="size-4 shrink-0" aria-hidden="true" />
          {profile.interview_location}
        </p>
      </div>

      {hasGuardianContact ? (
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
              : profile.guardian_notified_at
                ? `Reenviar e-mail (enviado em ${formatFullDate(profile.guardian_notified_at)})`
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
