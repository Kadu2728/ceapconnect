import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combina e mescla classes Tailwind com segurança, resolvendo conflitos
 * entre classes condicionais (ex.: `p-2` vs `p-4`).
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
