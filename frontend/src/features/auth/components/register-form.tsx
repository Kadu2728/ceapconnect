"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { Controller, useForm, useWatch } from "react-hook-form";

import { toast } from "@/components/feedback/toast/toast-store";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";

import { PasswordInput } from "@/features/auth/components/password-input";
import { PasswordStrengthMeter } from "@/features/auth/components/password-strength-meter";
import { useRegister } from "@/features/auth/hooks/use-register";
import { registerSchema, type RegisterFormValues } from "@/features/auth/types/schemas";
import { formatCpf } from "@/features/auth/utils/cpf";
import { onlyDigits } from "@/features/auth/utils/digits";
import { formatPhone } from "@/features/auth/utils/phone";

const DEFAULT_VALUES: RegisterFormValues = {
  name: "",
  email: "",
  cpf: "",
  phone: "",
  password: "",
  passwordConfirmation: "",
  acceptTerms: false,
};

/**
 * Formulário de cadastro (USER_FLOW.md → "Cadastro").
 *
 * Validação client-side (Zod) espelha as regras do backend para dar
 * feedback instantâneo; o erro final de negócio (409 e-mail/CPF duplicado,
 * 422 de validação) chega via `mutation.error` e é exibido como erro geral
 * do formulário, associado por `role="alert"`.
 */
export function RegisterForm() {
  const router = useRouter();
  const registerMutation = useRegister();

  const {
    register,
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: DEFAULT_VALUES,
    mode: "onBlur",
  });

  const passwordValue = useWatch({ control, name: "password" });

  const onSubmit = handleSubmit((values) => {
    registerMutation.mutate(
      {
        name: values.name.trim(),
        email: values.email.trim().toLowerCase(),
        cpf: onlyDigits(values.cpf),
        phone: onlyDigits(values.phone),
        password: values.password,
        password_confirmation: values.passwordConfirmation,
      },
      {
        onSuccess: () => {
          toast.success("Conta criada com sucesso!", {
            description: "Faça login para continuar sua jornada.",
          });
          router.push("/login?registered=1");
        },
        onError: (error) => {
          setError("root", { message: error.message });
        },
      },
    );
  });

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-5">
      <FormField id="name" label="Nome completo" error={errors.name?.message} required>
        <Input
          id="name"
          autoComplete="name"
          placeholder="Seu nome completo"
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? "name-error" : undefined}
          {...register("name")}
        />
      </FormField>

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

      <div className="grid gap-5 sm:grid-cols-2">
        <FormField id="cpf" label="CPF" error={errors.cpf?.message} required>
          <Controller
            control={control}
            name="cpf"
            render={({ field }) => (
              <Input
                id="cpf"
                inputMode="numeric"
                autoComplete="off"
                placeholder="000.000.000-00"
                value={field.value}
                onChange={(event) => field.onChange(formatCpf(event.target.value))}
                onBlur={field.onBlur}
                aria-invalid={!!errors.cpf}
                aria-describedby={errors.cpf ? "cpf-error" : undefined}
              />
            )}
          />
        </FormField>

        <FormField id="phone" label="Telefone" error={errors.phone?.message} required>
          <Controller
            control={control}
            name="phone"
            render={({ field }) => (
              <Input
                id="phone"
                inputMode="numeric"
                autoComplete="tel"
                placeholder="(00) 00000-0000"
                value={field.value}
                onChange={(event) => field.onChange(formatPhone(event.target.value))}
                onBlur={field.onBlur}
                aria-invalid={!!errors.phone}
                aria-describedby={errors.phone ? "phone-error" : undefined}
              />
            )}
          />
        </FormField>
      </div>

      <FormField
        id="password"
        label="Senha"
        error={errors.password?.message}
        description="Mínimo de 8 caracteres."
        required
      >
        <PasswordInput
          id="password"
          autoComplete="new-password"
          placeholder="••••••••"
          aria-invalid={!!errors.password}
          aria-describedby={errors.password ? "password-error" : "password-description"}
          {...register("password")}
        />
        <PasswordStrengthMeter password={passwordValue} />
      </FormField>

      <FormField
        id="passwordConfirmation"
        label="Confirmar senha"
        error={errors.passwordConfirmation?.message}
        required
      >
        <PasswordInput
          id="passwordConfirmation"
          autoComplete="new-password"
          placeholder="••••••••"
          aria-invalid={!!errors.passwordConfirmation}
          aria-describedby={
            errors.passwordConfirmation ? "passwordConfirmation-error" : undefined
          }
          {...register("passwordConfirmation")}
        />
      </FormField>

      <div className="flex flex-col gap-1.5">
        <label className="flex cursor-pointer items-start gap-3 text-sm">
          <Checkbox
            aria-invalid={!!errors.acceptTerms}
            aria-describedby={errors.acceptTerms ? "acceptTerms-error" : undefined}
            {...register("acceptTerms")}
          />
          <span className="text-muted-foreground">
            Li e aceito os{" "}
            <span className="font-medium text-foreground">Termos de Uso</span> e a{" "}
            <span className="font-medium text-foreground">Política de Privacidade</span>{" "}
            do CEAP Connect.
          </span>
        </label>
        {errors.acceptTerms ? (
          <p
            id="acceptTerms-error"
            role="alert"
            className="text-xs font-medium text-destructive"
          >
            {errors.acceptTerms.message}
          </p>
        ) : null}
      </div>

      {errors.root?.message ? (
        <p
          role="alert"
          className="rounded-md bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive"
        >
          {errors.root.message}
        </p>
      ) : null}

      <Button
        type="submit"
        size="lg"
        disabled={registerMutation.isPending}
        className="mt-2"
      >
        {registerMutation.isPending ? (
          <>
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
            Criando conta...
          </>
        ) : (
          "Criar minha conta"
        )}
      </Button>
    </form>
  );
}
