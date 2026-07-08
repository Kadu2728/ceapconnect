/**
 * Contratos genéricos de resposta da API (FastAPI).
 *
 * Tipos específicos de domínio (ex.: `Missao`, `Conquista`) devem viver em
 * `features/<feature>/types`, nunca aqui — este arquivo é só infraestrutura.
 */

/**
 * Envelope padrão de resposta da API (API_GUIDELINES.md: "success, message,
 * data, meta"), compartilhado por todas as features. Definir aqui evita
 * redefinir a mesma forma em `features/auth`, `features/dashboard` e em toda
 * EPIC futura que consumir a API.
 */
export interface ApiEnvelope<TData> {
  success: boolean;
  message: string;
  data: TData;
  meta?: Record<string, unknown> | null;
}

export interface ApiError {
  message: string;
  code: string;
  statusCode: number;
}

export interface PaginatedResponse<TItem> {
  items: TItem[];
  total: number;
  page: number;
  pageSize: number;
}
