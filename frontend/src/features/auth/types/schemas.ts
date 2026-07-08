import { z } from "zod";

import { isValidCpf } from "@/features/auth/utils/cpf";
import { onlyDigits } from "@/features/auth/utils/digits";

/**
 * Schemas Zod do domínio de autenticação — espelham no client as mesmas
 * regras aplicadas pelo backend (mínimo de 8 caracteres, CPF válido, senhas
 * coincidentes), para dar feedback imediato sem esperar a resposta da API.
 * A validação do backend continua sendo a autoridade final (ex.: 409/422).
 */

export const registerSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(3, "Informe seu nome completo.")
      .max(120, "Nome muito longo."),
    email: z.string().trim().min(1, "Informe seu e-mail.").email("E-mail inválido."),
    cpf: z
      .string()
      .min(1, "Informe seu CPF.")
      .refine((value) => isValidCpf(value), { message: "CPF inválido." }),
    phone: z
      .string()
      .min(1, "Informe seu telefone.")
      .refine((value) => onlyDigits(value).length >= 10, {
        message: "Telefone inválido.",
      }),
    password: z
      .string()
      .min(8, "A senha deve ter no mínimo 8 caracteres.")
      .max(72, "Senha muito longa."),
    passwordConfirmation: z.string().min(1, "Confirme sua senha."),
    acceptTerms: z.boolean().refine((value) => value === true, {
      message: "Você precisa aceitar os termos para continuar.",
    }),
  })
  .refine((data) => data.password === data.passwordConfirmation, {
    message: "As senhas não coincidem.",
    path: ["passwordConfirmation"],
  });

export type RegisterFormValues = z.infer<typeof registerSchema>;

export const loginSchema = z.object({
  email: z.string().trim().min(1, "Informe seu e-mail.").email("E-mail inválido."),
  password: z.string().min(1, "Informe sua senha."),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
