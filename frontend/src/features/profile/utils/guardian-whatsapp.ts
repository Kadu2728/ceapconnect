import { formatFullDate } from "@/features/dashboard/utils/date";
import type { Profile } from "@/features/profile/types/profile.types";

/**
 * Monta um link `wa.me` com a mensagem já preenchida, na voz do candidato —
 * puramente client-side, sem chamada ao backend e sem depender de nenhuma
 * integração paga (é o WhatsApp do próprio celular do candidato).
 *
 * Sem o telefone do responsável cadastrado, omite o número: o WhatsApp abre
 * o seletor de contatos em vez de travar a ação.
 */
export function buildGuardianWhatsAppLink(
  candidateName: string,
  profile: Profile,
): string {
  const dateLabel = profile.interview_date
    ? formatFullDate(profile.interview_date)
    : "em breve (data a confirmar)";
  const message =
    `Oi! Aqui é o(a) ${candidateName}. Minha entrevista do processo seletivo do ` +
    `CEAP foi marcada para ${dateLabel}, na ${profile.interview_location}. ` +
    "Você pode vir comigo? 💚";
  const encodedMessage = encodeURIComponent(message);

  if (profile.guardian_phone) {
    return `https://wa.me/55${profile.guardian_phone}?text=${encodedMessage}`;
  }
  return `https://wa.me/?text=${encodedMessage}`;
}
