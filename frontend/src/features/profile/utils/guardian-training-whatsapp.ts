import { formatFullDate } from "@/features/dashboard/utils/date";
import type { Profile } from "@/features/profile/types/profile.types";

/**
 * Monta um link `wa.me` com a mensagem já preenchida, na voz do candidato —
 * puramente client-side, sem chamada ao backend (mesmo padrão de
 * `guardian-whatsapp.ts`, mas para a formação obrigatória). Inclui o link
 * do Portal do Responsável: é a única etapa autoconfirmável pelo próprio
 * responsável, então o link precisa ir junto da mensagem.
 */
export function buildGuardianTrainingWhatsAppLink(
  candidateName: string,
  profile: Profile,
): string {
  const dateLabel = profile.guardian_training_date
    ? formatFullDate(profile.guardian_training_date)
    : "em breve (data a confirmar)";
  const message =
    `Oi! Aqui é o(a) ${candidateName}. A formação obrigatória do processo seletivo do ` +
    `CEAP foi marcada para ${dateLabel}, na ${profile.interview_location}. ` +
    `Você pode confirmar presença aqui: ${profile.guardian_portal_url ?? ""} 💚`;
  const encodedMessage = encodeURIComponent(message);

  if (profile.guardian_phone) {
    return `https://wa.me/55${profile.guardian_phone}?text=${encodedMessage}`;
  }
  return `https://wa.me/?text=${encodedMessage}`;
}
