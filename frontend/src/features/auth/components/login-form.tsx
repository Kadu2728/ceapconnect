"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";

import { PasswordInput } from "@/features/auth/components/password-input";
import { useLogin } from "@/features/auth/hooks/use-login";
import { loginSchema, type LoginFormValues } from "@/features/auth/types/schemas";

const DEFAULT_VALUES: LoginFormValues = { email: "", password: "" };

/**
 * Formulário de login (USER_FLOW.md → "Primeiro Login").
 *
 * Erro 401 vira sempre a mesma mensagem genérica ("E-mail ou senha
 * inválidos") — nunca revelamos qual dos dois campos está incorreto, prática
 * de segurança padrão para evitar enumeração de e-mails cadastrados.
 */
export function LoginForm() {
  const router = useRouter();
  const loginMutation = useLogin();

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: DEFAULT_VALUES,
    mode: "onBlur",
  });

  const onSubmit = handleSubmit((values) => {
    loginMutation.mutate(values, {
      onSuccess: (data) => {
        router.push(data.user.role === "guardian" ? "/area-responsavel" : "/dashboard");
      },
      onError: (error) => {
        setError("root", { message: error.message });
      },
    });
  });

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-5">
      <FormField id="email" label="E-mail" error={errors.email?.message} required>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          placeholder="voce@email.com"
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? "email-error" : undefined}
          {...register("email")}
        />
      </FormField>

      <FormField id="password" label="Senha" error={errors.password?.message} required>
        <PasswordInput
          id="password"
          autoComplete="current-password"
          placeholder="••••••••"
          aria-invalid={!!errors.password}
          aria-describedby={errors.password ? "password-error" : undefined}
          {...register("password")}
        />
      </FormField>

      {errors.root?.message ? (
        <p
          role="alert"
          className="rounded-md bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive"
        >
          {errors.root.message}
        </p>
      ) : null}

      <Button type="submit" size="lg" disabled={loginMutation.isPending} className="mt-2">
        {loginMutation.isPending ? (
          <>
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
            Entrando...
          </>
        ) : (
          "Entrar"
        )}
      </Button>
    </form>
  );
}
