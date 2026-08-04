"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { onlyDigits } from "@/features/auth/utils/digits";
import { formatPhone } from "@/features/auth/utils/phone";
import { useUpdateProfile } from "@/features/profile/hooks/use-update-profile";
import type { Profile } from "@/features/profile/types/profile.types";

interface ProfileEditFormProps {
  profile: Profile;
}

/**
 * Formulário de edição do perfil. Nome e telefone são editáveis; e-mail e CPF
 * são somente leitura (identidade da conta). O botão salvar só habilita quando
 * há mudança válida — evita chamadas desnecessárias e reforça o controle do usuário.
 */
export function ProfileEditForm({ profile }: ProfileEditFormProps) {
  const [name, setName] = useState(profile.name);
  const [phone, setPhone] = useState(formatPhone(profile.phone));
  const updateMutation = useUpdateProfile();

  const phoneDigits = onlyDigits(phone);
  const nameValid = name.trim().length >= 2;
  const phoneValid = phoneDigits.length === 10 || phoneDigits.length === 11;
  const changed = name.trim() !== profile.name || phoneDigits !== profile.phone;
  const canSave = nameValid && phoneValid && changed && !updateMutation.isPending;

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSave) return;
    updateMutation.mutate({ name: name.trim(), phone: phoneDigits });
  }

  return (
    <Card className="gap-5">
      <div className="px-6">
        <h3 className="font-semibold">Dados da conta</h3>
        <p className="text-sm text-muted-foreground">
          Atualize seus dados de contato. E-mail e CPF são fixos por segurança.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4 px-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="profile-name">Nome completo</Label>
            <Input
              id="profile-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              maxLength={150}
              aria-invalid={!nameValid}
              autoComplete="name"
            />
            {!nameValid ? (
              <span className="text-xs text-destructive">Informe seu nome completo.</span>
            ) : null}
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="profile-phone">Telefone</Label>
            <Input
              id="profile-phone"
              inputMode="numeric"
              value={phone}
              onChange={(event) => setPhone(formatPhone(event.target.value))}
              placeholder="(11) 90000-0000"
              aria-invalid={phone.length > 0 && !phoneValid}
              autoComplete="tel"
            />
            {phone.length > 0 && !phoneValid ? (
              <span className="text-xs text-destructive">Telefone incompleto.</span>
            ) : null}
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="profile-email">E-mail</Label>
            <Input id="profile-email" value={profile.email} disabled readOnly />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="profile-cpf">CPF</Label>
            <Input id="profile-cpf" value={profile.cpf_masked} disabled readOnly />
          </div>
        </div>

        <div>
          <Button type="submit" disabled={!canSave}>
            {updateMutation.isPending ? "Salvando…" : "Salvar alterações"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
