"use client";

import { useMutation } from "@tanstack/react-query";

import { registerUser } from "@/features/auth/services/auth.service";
import type {
  RegisterRequest,
  RegisterResponseData,
} from "@/features/auth/types/auth.types";
import {
  extractApiErrorMessage,
  getApiErrorStatus,
} from "@/features/auth/utils/api-error";

const DEFAULT_ERROR_MESSAGE = "Não foi possível concluir seu cadastro. Tente novamente.";
const EMAIL_OR_CPF_TAKEN_MESSAGE =
  "Este e-mail ou CPF já está cadastrado. Faça login ou utilize outro e-mail.";

/**
 * Mutation de cadastro (`POST /auth/register`).
 *
 * Normaliza o erro da API em uma única mensagem amigável antes de propagar
 * — o componente só precisa ler `mutation.error?.message`, nunca inspecionar
 * a resposta HTTP crua (409 = e-mail/CPF duplicado, demais = mensagem
 * genérica ou de validação vinda do backend).
 */
export function useRegister() {
  return useMutation<RegisterResponseData, Error, RegisterRequest>({
    mutationFn: async (payload) => {
      try {
        return await registerUser(payload);
      } catch (error) {
        const status = getApiErrorStatus(error);
        const message =
          status === 409
            ? EMAIL_OR_CPF_TAKEN_MESSAGE
            : extractApiErrorMessage(error, DEFAULT_ERROR_MESSAGE);
        throw new Error(message);
      }
    },
  });
}
