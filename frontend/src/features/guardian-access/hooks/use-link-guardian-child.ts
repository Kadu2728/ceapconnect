"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  extractApiErrorMessage,
  getApiErrorStatus,
} from "@/features/auth/utils/api-error";
import { GUARDIAN_CHILDREN_QUERY_KEY } from "@/features/guardian-access/hooks/use-guardian-children";
import { linkGuardianChild } from "@/features/guardian-access/services/guardian-access.service";
import type {
  GuardianChildItem,
  GuardianLinkChildRequest,
} from "@/features/guardian-access/types/guardian-access.types";

const DEFAULT_ERROR_MESSAGE = "Não foi possível vincular este link. Tente novamente.";
const NOT_FOUND_MESSAGE = "Link inválido ou expirado.";

/**
 * Anexa mais um filho à conta já autenticada do responsável, pelo link
 * mágico enviado por e-mail/WhatsApp (o mesmo usado no Portal público) —
 * caso de dois irmãos no CEAP com o mesmo responsável.
 */
export function useLinkGuardianChild() {
  const queryClient = useQueryClient();

  return useMutation<GuardianChildItem, Error, GuardianLinkChildRequest>({
    mutationFn: async (payload) => {
      try {
        return await linkGuardianChild(payload);
      } catch (error) {
        const status = getApiErrorStatus(error);
        const message =
          status === 404
            ? NOT_FOUND_MESSAGE
            : extractApiErrorMessage(error, DEFAULT_ERROR_MESSAGE);
        throw new Error(message);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: GUARDIAN_CHILDREN_QUERY_KEY });
    },
  });
}
