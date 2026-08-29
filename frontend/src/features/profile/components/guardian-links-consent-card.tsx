"use client";

import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { formatFullDate } from "@/features/dashboard/utils/date";
import {
  useConsentGuardianLink,
  useRevokeGuardianLink,
} from "@/features/profile/hooks/use-guardian-link-consent";
import { useGuardianLinks } from "@/features/profile/hooks/use-guardian-links";
import type { GuardianConsentStatus } from "@/features/profile/types/profile.types";
import { cn } from "@/lib/utils";

const STATUS_LABEL: Record<GuardianConsentStatus, string> = {
  not_required: "Autorizado",
  pending: "Aguardando sua autorização",
  granted: "Autorizado",
  revoked: "Acesso revogado",
};

const STATUS_CLASS: Record<GuardianConsentStatus, string> = {
  not_required: "bg-success/10 text-success",
  pending: "bg-warning/10 text-warning",
  granted: "bg-success/10 text-success",
  revoked: "bg-muted text-muted-foreground",
};

/**
 * Consentimento do candidato ao vínculo do responsável (RBAC do responsável
 * — fase C): quem pediu para acompanhar a jornada, e a decisão de
 * autorizar/revogar é sempre do candidato, nunca automática (não há coleta
 * de data de nascimento em lugar nenhum do sistema para o backend decidir
 * maioridade sozinho — ver `app.models.guardian_candidate_link`).
 *
 * Some da tela quando não há nenhum vínculo — a maioria dos candidatos não
 * terá nenhum pedido ainda, e um card vazio só adicionaria ruído.
 */
export function GuardianLinksConsentCard() {
  const linksQuery = useGuardianLinks();
  const consentMutation = useConsentGuardianLink();
  const revokeMutation = useRevokeGuardianLink();

  const links = linksQuery.data?.links ?? [];
  if (linksQuery.isPending || linksQuery.isError || links.length === 0) {
    return null;
  }

  return (
    <Card className="gap-4">
      <div className="px-6">
        <h3 className="font-semibold">Responsáveis com acesso à sua jornada</h3>
        <p className="text-sm text-muted-foreground">
          Só você decide quem acompanha — nunca a nota ou o desempenho, apenas o
          progresso.
        </p>
      </div>

      <ul className="flex flex-col gap-3 px-6">
        {links.map((link) => {
          const isPending =
            (consentMutation.isPending && consentMutation.variables === link.id) ||
            (revokeMutation.isPending && revokeMutation.variables === link.id);
          const canConsent =
            link.consent_status === "pending" || link.consent_status === "revoked";
          const canRevoke = link.consent_status === "granted";

          return (
            <li
              key={link.id}
              className="flex flex-col gap-3 rounded-xl border bg-muted/30 p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p className="font-medium">{link.guardian_name}</p>
                <p className="text-xs text-muted-foreground">{link.guardian_email}</p>
                <p className="text-xs text-muted-foreground">
                  Pedido em {formatFullDate(link.created_at)}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    "rounded-full px-2.5 py-1 text-xs font-medium",
                    STATUS_CLASS[link.consent_status],
                  )}
                >
                  {STATUS_LABEL[link.consent_status]}
                </span>

                {canConsent ? (
                  <Button
                    size="sm"
                    disabled={isPending}
                    onClick={() => consentMutation.mutate(link.id)}
                  >
                    {isPending ? (
                      <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
                    ) : (
                      "Autorizar"
                    )}
                  </Button>
                ) : null}

                {canRevoke ? (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={isPending}
                    onClick={() => revokeMutation.mutate(link.id)}
                  >
                    {isPending ? (
                      <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
                    ) : (
                      "Revogar"
                    )}
                  </Button>
                ) : null}
              </div>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}
