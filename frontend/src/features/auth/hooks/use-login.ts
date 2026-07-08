"use client";

import { useMutation } from "@tanstack/react-query";

import { loginUser } from "@/features/auth/services/auth.service";
import { useAuthStore } from "@/features/auth/store/auth-store";
import type { LoginRequest, LoginResponseData } from "@/features/auth/types/auth.types";
import {
  extractApiErrorMessage,
  getApiErrorStatus,
} from "@/features/auth/utils/api-error";

const DEFAULT_ERROR_MESSAGE = "Não foi possível entrar. Tente novamente em instantes.";
const INVALID_CREDENTIALS_MESSAGE = "E-mail ou senha inválidos.";

/**
 * Mutation de login (`POST /auth/login`).
 *
 * Em caso de sucesso, já persiste a sessão (tokens + usuário) na store
 * global — o componente de UI não manipula tokens diretamente, apenas
 * decide para onde navegar após a mutation resolver.
 */
export function useLogin() {
  const setSession = useAuthStore((state) => state.setSession);

  return useMutation<LoginResponseData, Error, LoginRequest>({
    mutationFn: async (payload) => {
      try {
        return await loginUser(payload);
      } catch (error) {
        const status = getApiErrorStatus(error);
        const message =
          status === 401
            ? INVALID_CREDENTIALS_MESSAGE
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
    },
  });
}
