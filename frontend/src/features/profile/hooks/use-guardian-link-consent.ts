"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { toast } from "@/components/feedback/toast/toast-store";
import { extractApiErrorMessage } from "@/features/auth/utils/api-error";
import { GUARDIAN_LINKS_QUERY_KEY } from "@/features/profile/hooks/use-guardian-links";
import {
  consentGuardianLink,
  revokeGuardianLink,
} from "@/features/profile/services/profile.service";

/** Autoriza um responsável a acompanhar a jornada (`pending`/`revoked` → `granted`). */
export function useConsentGuardianLink() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: consentGuardianLink,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GUARDIAN_LINKS_QUERY_KEY });
      toast.success("Responsável autorizado!", {
        description: "Ele já pode acompanhar sua jornada pelo app.",
      });
    },
    onError: (error) => {
      toast.error("Não foi possível autorizar agora", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}

/** Revoga um vínculo já autorizado (`granted` → `revoked`) — o responsável perde acesso na hora. */
export function useRevokeGuardianLink() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: revokeGuardianLink,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GUARDIAN_LINKS_QUERY_KEY });
      toast.success("Acesso revogado.");
    },
    onError: (error) => {
      toast.error("Não foi possível revogar agora", {
        description: extractApiErrorMessage(error, "Tente novamente em instantes."),
      });
    },
  });
}
