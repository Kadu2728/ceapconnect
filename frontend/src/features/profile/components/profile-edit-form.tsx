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

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Formulário de edição do perfil. Nome e telefone são editáveis; e-mail e CPF
 * são somente leitura (identidade da conta). O botão salvar só habilita quando
 * há mudança válida — evita chamadas desnecessárias e reforça o controle do usuário.
 *
 * Também reúne o contato do responsável (EPIC 17) — todos os três campos são
 * opcionais, mas quando preenchidos precisam ser válidos, já que alimentam o
 * aviso por e-mail/WhatsApp da entrevista.
 */
export function ProfileEditForm({ profile }: ProfileEditFormProps) {
  const [name, setName] = useState(profile.name);
  const [phone, setPhone] = useState(formatPhone(profile.phone));
  const [guardianName, setGuardianName] = useState(profile.guardian_name ?? "");
  const [guardianPhone, setGuardianPhone] = useState(
    formatPhone(profile.guardian_phone ?? ""),
  );
  const [guardianEmail, setGuardianEmail] = useState(profile.guardian_email ?? "");
  const updateMutation = useUpdateProfile();

  const phoneDigits = onlyDigits(phone);
  const guardianPhoneDigits = onlyDigits(guardianPhone);
  const nameValid = name.trim().length >= 2;
  const phoneValid = phoneDigits.length === 10 || phoneDigits.length === 11;
  const guardianPhoneValid =
    guardianPhoneDigits.length === 0 ||
    guardianPhoneDigits.length === 10 ||
    guardianPhoneDigits.length === 11;
  const guardianEmailValid =
    guardianEmail.trim().length === 0 || EMAIL_RE.test(guardianEmail);

  const changed =
    name.trim() !== profile.name ||
    phoneDigits !== profile.phone ||
    guardianName.trim() !== (profile.guardian_name ?? "") ||
    guardianPhoneDigits !== (profile.guardian_phone ?? "") ||
    guardianEmail.trim() !== (profile.guardian_email ?? "");

  const canSave =
    nameValid &&
    phoneValid &&
    guardianPhoneValid &&
    guardianEmailValid &&
    changed &&
    !updateMutation.isPending;

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSave) return;
    updateMutation.mutate({
      name: name.trim(),
      phone: phoneDigits,
      guardian_name: guardianName.trim() || null,
      guardian_phone: guardianPhoneDigits || null,
      guardian_email: guardianEmail.trim() || null,
    });
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

        <div className="border-t pt-4">
          <h4 className="font-semibold">Responsável</h4>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Quem te acompanha na entrevista — usado para o aviso por e-mail e WhatsApp.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="guardian-name">Nome do responsável</Label>
            <Input
              id="guardian-name"
              value={guardianName}
              onChange={(event) => setGuardianName(event.target.value)}
              maxLength={150}
              autoComplete="off"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="guardian-phone">Telefone do responsável</Label>
            <Input
              id="guardian-phone"
              inputMode="numeric"
              value={guardianPhone}
              onChange={(event) => setGuardianPhone(formatPhone(event.target.value))}
              placeholder="(11) 90000-0000"
              aria-invalid={guardianPhone.length > 0 && !guardianPhoneValid}
              autoComplete="off"
            />
            {guardianPhone.length > 0 && !guardianPhoneValid ? (
              <span className="text-xs text-destructive">Telefone incompleto.</span>
            ) : null}
          </div>

          <div className="flex flex-col gap-1.5 sm:col-span-2">
            <Label htmlFor="guardian-email">E-mail do responsável</Label>
            <Input
              id="guardian-email"
              type="email"
              value={guardianEmail}
              onChange={(event) => setGuardianEmail(event.target.value)}
              placeholder="responsavel@exemplo.com"
              aria-invalid={guardianEmail.length > 0 && !guardianEmailValid}
              autoComplete="off"
            />
            {guardianEmail.length > 0 && !guardianEmailValid ? (
              <span className="text-xs text-destructive">E-mail inválido.</span>
            ) : null}
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
