import { onlyDigits } from "@/features/auth/utils/digits";

const PHONE_MAX_LENGTH = 11;

/**
 * Aplica máscara de telefone brasileiro progressivamente: `(00) 0000-0000`
 * para fixo (10 dígitos) e `(00) 00000-0000` para celular (11 dígitos),
 * detectando automaticamente qual formato usar pela quantidade já digitada.
 */
export function formatPhone(value: string): string {
  const digits = onlyDigits(value).slice(0, PHONE_MAX_LENGTH);

  if (digits.length === 0) return "";
  if (digits.length <= 2) return `(${digits}`;

  const ddd = digits.slice(0, 2);
  const rest = digits.slice(2);

  if (rest.length <= 4) return `(${ddd}) ${rest}`;
  if (rest.length <= 8) return `(${ddd}) ${rest.slice(0, 4)}-${rest.slice(4)}`;
  return `(${ddd}) ${rest.slice(0, 5)}-${rest.slice(5)}`;
}
