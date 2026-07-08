import { onlyDigits } from "@/features/auth/utils/digits";

const CPF_LENGTH = 11;

/**
 * Aplica a máscara `000.000.000-00` progressivamente enquanto o usuário
 * digita, sem exigir que o valor já esteja completo.
 */
export function formatCpf(value: string): string {
  const digits = onlyDigits(value).slice(0, CPF_LENGTH);

  const parts = [
    digits.slice(0, 3),
    digits.slice(3, 6),
    digits.slice(6, 9),
    digits.slice(9, 11),
  ].filter((part) => part.length > 0);

  if (parts.length <= 1) return parts[0] ?? "";
  if (parts.length === 2) return `${parts[0]}.${parts[1]}`;
  if (parts.length === 3) return `${parts[0]}.${parts[1]}.${parts[2]}`;
  return `${parts[0]}.${parts[1]}.${parts[2]}-${parts[3]}`;
}

function calculateCheckDigit(base: string, startingFactor: number): number {
  let total = 0;
  let factor = startingFactor;

  for (const digit of base) {
    total += Number(digit) * factor;
    factor -= 1;
  }

  const remainder = (total * 10) % 11;
  return remainder === 10 ? 0 : remainder;
}

/**
 * Valida um CPF aplicando o algoritmo oficial de dígito verificador
 * (Módulo 11) usado pela Receita Federal — uma regex de formato não é
 * suficiente, pois `123.456.789-00` passaria no formato sem ser um CPF
 * matematicamente válido.
 *
 * Também rejeita sequências de dígitos repetidos (ex.: "111.111.111-11"),
 * que satisfazem o algoritmo mas nunca são emitidas na prática.
 */
export function isValidCpf(value: string): boolean {
  const digits = onlyDigits(value);

  if (digits.length !== CPF_LENGTH) return false;
  if (/^(\d)\1{10}$/.test(digits)) return false;

  const firstCheckDigit = calculateCheckDigit(digits.slice(0, 9), 10);
  if (firstCheckDigit !== Number(digits[9])) return false;

  const secondCheckDigit = calculateCheckDigit(digits.slice(0, 10), 11);
  if (secondCheckDigit !== Number(digits[10])) return false;

  return true;
}
