/**
 * Remove qualquer caractere que não seja dígito (0-9) de uma string.
 *
 * Compartilhado entre máscaras de CPF e telefone — ambas precisam do valor
 * "cru" (sem pontuação) tanto para formatar progressivamente quanto para
 * enviar ao backend, que espera os campos sem máscara.
 */
export function onlyDigits(value: string): string {
  return value.replace(/\D/g, "");
}
