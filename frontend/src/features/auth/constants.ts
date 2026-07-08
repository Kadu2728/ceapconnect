/**
 * Caminhos das rotas de autenticação (EPIC 02), compartilhados entre o
 * service da feature e o interceptor global do Axios (`src/lib/axios.ts`).
 *
 * Centralizar aqui evita duplicar literais de string entre as duas camadas
 * e garante que uma mudança de rota no backend precise ser atualizada em um
 * único lugar.
 */
export const AUTH_ENDPOINTS = {
  register: "/api/v1/auth/register",
  login: "/api/v1/auth/login",
  refresh: "/api/v1/auth/refresh",
  me: "/api/v1/users/me",
} as const;
