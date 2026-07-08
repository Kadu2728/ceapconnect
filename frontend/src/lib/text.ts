/**
 * Deriva até duas iniciais maiúsculas a partir de um nome completo, para
 * exibir em avatares sem foto (fallback). Ex.: "Maria Silva" -> "MS".
 *
 * Usado hoje pela navbar autenticada; reutilizável pelo Perfil (EPIC 09)
 * quando o candidato ainda não tiver enviado uma foto.
 */
export function getInitials(fullName: string): string {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";

  const first = parts[0]?.[0] ?? "";
  const last = parts.length > 1 ? (parts[parts.length - 1]?.[0] ?? "") : "";

  return `${first}${last}`.toUpperCase();
}
