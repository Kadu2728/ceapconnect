"use client";

import { Loader2, Plus } from "lucide-react";
import { useState } from "react";

import { toast } from "@/components/feedback/toast/toast-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLinkGuardianChild } from "@/features/guardian-access/hooks/use-link-guardian-child";

/**
 * Anexa mais um filho à conta já autenticada, colando o mesmo link mágico
 * que o candidato enviou por e-mail/WhatsApp — caso de dois irmãos no CEAP
 * com o mesmo responsável (ver `guardian_access_service.link_child`).
 */
export function LinkGuardianChildForm() {
  const [expanded, setExpanded] = useState(false);
  const [link, setLink] = useState("");
  const linkMutation = useLinkGuardianChild();

  const extractToken = (value: string): string => {
    const trimmed = value.trim();
    const lastSegment = trimmed.split("/").filter(Boolean).pop();
    return lastSegment ?? trimmed;
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const token = extractToken(link);
    if (!token) return;

    linkMutation.mutate(
      { token },
      {
        onSuccess: (child) => {
          toast.success(`${child.name} vinculado com sucesso!`);
          setLink("");
          setExpanded(false);
        },
        onError: (error) => {
          toast.error(error.message);
        },
      },
    );
  };

  if (!expanded) {
    return (
      <Button variant="outline" onClick={() => setExpanded(true)} className="w-fit">
        <Plus className="size-4" aria-hidden="true" />
        Vincular outro candidato
      </Button>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-2xl border bg-card p-5 shadow-sm sm:flex-row sm:items-end"
    >
      <div className="flex-1">
        <label htmlFor="link-child-token" className="mb-1.5 block text-sm font-medium">
          Link do outro candidato
        </label>
        <Input
          id="link-child-token"
          value={link}
          onChange={(event) => setLink(event.target.value)}
          placeholder="Cole aqui o link enviado por e-mail/WhatsApp"
          autoComplete="off"
        />
      </div>
      <div className="flex gap-2">
        <Button type="submit" disabled={linkMutation.isPending || !link.trim()}>
          {linkMutation.isPending ? (
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
          ) : (
            "Vincular"
          )}
        </Button>
        <Button type="button" variant="ghost" onClick={() => setExpanded(false)}>
          Cancelar
        </Button>
      </div>
    </form>
  );
}
