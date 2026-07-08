export type PasswordStrength = "fraca" | "média" | "forte";

/**
 * Heurística simples de força de senha, usada apenas como feedback visual
 * incentivando senhas melhores. A única regra que de fato bloqueia o envio
 * do formulário é o mínimo de 8 caracteres (validado via Zod), espelhando a
 * regra do backend — nunca exigimos maiúsculas/caracteres especiais aqui
 * para não divergir do contrato da API com uma regra client-side mais
 * restritiva do que a real.
 */
export function getPasswordStrength(password: string): PasswordStrength | null {
  if (password.length === 0) return null;
  if (password.length < 8) return "fraca";

  let score = 0;
  if (password.length >= 12) score += 1;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (score <= 1) return "fraca";
  if (score === 2) return "média";
  return "forte";
}
