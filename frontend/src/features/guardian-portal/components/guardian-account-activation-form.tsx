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
import { registerSchema, type RegisterFormValues } from "@/features/auth/types/schemas";
import { formatCpf } from "@/features/auth/utils/cpf";
import { onlyDigits } from "@/features/auth/utils/digits";
import { formatPhone } from "@/features/auth/utils/phone";
import { useActivateGuardianAccount } from "@/features/guardian-portal/hooks/use-activate-guardian-account";

const DEFAULT_VALUES: RegisterFormValues = {
  name: "",
  email: "",
  cpf: "",
  phone: "",
  password: "",
  passwordConfirmation: "",
  acceptTerms: false,
};

interface GuardianAccountActivationFormProps {
  token: string;
}

/**
 * Formulário de ativação de conta do responsável (RBAC do responsável —
 * fase B), embutido no Portal do Responsável (`/responsavel/[token]`).
 *
 * Reaproveita `registerSchema`/`RegisterFormValues` do cadastro de candidato
 * (`features/auth/types/schemas.ts`) — os campos e as regras de validação
 * são idênticos, só o destino do submit (`activate`, não `register`) e o
 * pós-sucesso (login imediato, não redirecionar para `/login`) diferem.
 */
export function GuardianAccountActivationForm({
  token,
}: GuardianAccountActivationFormProps) {
  const router = useRouter();
  const activateMutation = useActivateGuardianAccount(token);

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
    activateMutation.mutate(
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
            description:
              "Agora você pode acompanhar a jornada do seu candidato por aqui.",
          });
          router.push("/area-responsavel");
        },
        onError: (error) => {
          setError("root", { message: error.message });
        },
      },
    );
  });

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
      <FormField
        id="guardian-name"
        label="Nome completo"
        error={errors.name?.message}
        required
      >
        <Input
          id="guardian-name"
          autoComplete="name"
          placeholder="Seu nome completo"
          aria-invalid={!!errors.name}
          {...register("name")}
        />
      </FormField>

      <FormField
        id="guardian-email"
        label="E-mail"
        error={errors.email?.message}
        required
      >
        <Input
          id="guardian-email"
          type="email"
          autoComplete="email"
          placeholder="voce@email.com"
          aria-invalid={!!errors.email}
          {...register("email")}
        />
      </FormField>

      <div className="grid gap-4 sm:grid-cols-2">
        <FormField id="guardian-cpf" label="CPF" error={errors.cpf?.message} required>
          <Controller
            control={control}
            name="cpf"
            render={({ field }) => (
              <Input
                id="guardian-cpf"
                inputMode="numeric"
                autoComplete="off"
                placeholder="000.000.000-00"
                value={field.value}
                onChange={(event) => field.onChange(formatCpf(event.target.value))}
                onBlur={field.onBlur}
                aria-invalid={!!errors.cpf}
              />
            )}
          />
        </FormField>

        <FormField
          id="guardian-phone"
          label="Telefone"
          error={errors.phone?.message}
          required
        >
          <Controller
            control={control}
            name="phone"
            render={({ field }) => (
              <Input
                id="guardian-phone"
                inputMode="numeric"
                autoComplete="tel"
                placeholder="(00) 00000-0000"
                value={field.value}
                onChange={(event) => field.onChange(formatPhone(event.target.value))}
                onBlur={field.onBlur}
                aria-invalid={!!errors.phone}
              />
            )}
          />
        </FormField>
      </div>

      <FormField
        id="guardian-password"
        label="Senha"
        error={errors.password?.message}
        description="Mínimo de 8 caracteres."
        required
      >
        <PasswordInput
          id="guardian-password"
          autoComplete="new-password"
          placeholder="••••••••"
          aria-invalid={!!errors.password}
          {...register("password")}
        />
        <PasswordStrengthMeter password={passwordValue} />
      </FormField>

      <FormField
        id="guardian-passwordConfirmation"
        label="Confirmar senha"
        error={errors.passwordConfirmation?.message}
        required
      >
        <PasswordInput
          id="guardian-passwordConfirmation"
          autoComplete="new-password"
          placeholder="••••••••"
          aria-invalid={!!errors.passwordConfirmation}
          {...register("passwordConfirmation")}
        />
      </FormField>

      <label className="flex cursor-pointer items-start gap-3 text-sm">
        <Checkbox aria-invalid={!!errors.acceptTerms} {...register("acceptTerms")} />
        <span className="text-muted-foreground">
          Li e aceito os{" "}
          <span className="font-medium text-foreground">Termos de Uso</span> e a{" "}
          <span className="font-medium text-foreground">Política de Privacidade</span> do
          CEAP Connect.
        </span>
      </label>
      {errors.acceptTerms ? (
        <p role="alert" className="-mt-2 text-xs font-medium text-destructive">
          {errors.acceptTerms.message}
        </p>
      ) : null}

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
        disabled={activateMutation.isPending}
        className="mt-1"
      >
        {activateMutation.isPending ? (
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
