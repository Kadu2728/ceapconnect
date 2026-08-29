/**
 * Contratos de request/response da API de autenticação, espelhando
 * exatamente o contrato acordado com o backend (EPIC 02). Nomes de campo em
 * `snake_case` são mantidos como o backend os envia — a conversão para o
 * formato usado internamente pela UI acontece nos `services`, nunca aqui.
 */

/**
 * Envelope padrão de resposta da API (API_GUIDELINES.md).
 *
 * Reexportado aqui por compatibilidade — a definição real vive em
 * `@/types/api`, compartilhada por todas as features (evita redefinir o
 * mesmo contrato em cada domínio, ex.: `features/dashboard`).
 */
export type { ApiEnvelope } from "@/types/api";

export interface RegisterRequest {
  name: string;
  email: string;
  cpf: string;
  phone: string;
  password: string;
  password_confirmation: string;
}

export interface RegisterResponseData {
  id: string;
  name: string;
  email: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export type UserRole = "candidate" | "coordinator" | "admin" | "guardian";

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  is_admin: boolean;
  /** EPIC 14 — RBAC: define acesso ao Console de Intervenção (coordinator/admin). */
  role: UserRole;
}

export interface LoginResponseData {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  user: AuthUser;
}

export interface RefreshResponseData {
  access_token: string;
}

export interface CurrentUserResponseData {
  id: string;
  name: string;
  email: string;
  cpf: string;
  phone: string;
  created_at: string;
}
