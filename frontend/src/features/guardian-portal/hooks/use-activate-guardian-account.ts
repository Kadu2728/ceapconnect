"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";
import type { LoginResponseData } from "@/features/auth/types/auth.types";
import {
  extractApiErrorMessage,
  getApiErrorStatus,
} from "@/features/auth/utils/api-error";
import { GUARDIAN_PORTAL_QUERY_KEY } from "@/features/guardian-portal/hooks/use-guardian-portal";
import { activateGuardianAccount } from "@/features/guardian-portal/services/guardian-portal.service";
import type { GuardianAccountActivationRequest } from "@/features/guardian-portal/types/guardian-portal.types";

const DEFAULT_ERROR_MESSAGE = "Não foi possível criar sua conta. Tente novamente.";
const ALREADY_ACTIVE_MESSAGE =
  "Este link já foi usado para criar uma conta, ou o e-mail/CPF informado já está cadastrado.";

/**
 * Mutation de ativação de conta do responsável (`POST
 * /guardian-portal/{token}/activate`) — fase B do RBAC do responsável.
 *
 * Em caso de sucesso já persiste a sessão na store global (mesmo shape de
 * `useLogin`, o backend devolve o mesmo `TokenPairResponse`): o responsável
 * sai da tela de ativação já autenticado, sem precisar logar de novo.
 */
export function useActivateGuardianAccount(token: string) {
  const setSession = useAuthStore((state) => state.setSession);
  const queryClient = useQueryClient();

  return useMutation<LoginResponseData, Error, GuardianAccountActivationRequest>({
    mutationFn: async (payload) => {
      try {
        return await activateGuardianAccount(token, payload);
      } catch (error) {
        const status = getApiErrorStatus(error);
        const message =
          status === 409
            ? ALREADY_ACTIVE_MESSAGE
            : extractApiErrorMessage(error, DEFAULT_ERROR_MESSAGE);
        throw new Error(message);
      }
    },
    onSuccess: (data) => {
      setSession({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        user: data.user,
      });
      queryClient.invalidateQueries({ queryKey: GUARDIAN_PORTAL_QUERY_KEY(token) });
    },
  });
}
