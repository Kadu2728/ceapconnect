import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { AUTH_ENDPOINTS } from "@/features/auth/constants";
import { useAuthStore } from "@/features/auth/store/auth-store";
import type { ApiEnvelope, RefreshResponseData } from "@/features/auth/types/auth.types";

/**
 * Instância central do Axios utilizada pelos services de cada feature.
 *
 * Este módulo concentra configuração transversal de infraestrutura HTTP
 * (baseURL, timeout, interceptors). Tratamento de erro de negócio (ex.:
 * mensagens amigáveis por status) fica nos hooks da feature correspondente
 * (`features/auth/hooks`) — aqui só existe o contrato genérico: anexar o
 * token de sessão e renovar automaticamente quando ele expira.
 *
 * Este arquivo importa deliberadamente de `features/auth` (store e
 * constantes) — uma exceção pontual à regra geral de "lib nunca depende de
 * feature", justificada porque injetar/renovar o token é uma
 * responsabilidade inerente à própria infraestrutura HTTP, não uma regra de
 * negócio exclusiva da feature de autenticação.
 */
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  timeout: 15_000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { accessToken } = useAuthStore.getState();

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  /** Marca que esta requisição já tentou um refresh, evitando loop infinito. */
  _retry?: boolean;
}

/**
 * Compartilhada entre requisições concorrentes que recebem 401 ao mesmo
 * tempo, garantindo que apenas UMA chamada de refresh seja disparada.
 */
let pendingRefresh: Promise<string> | null = null;

function isAuthEndpoint(url: string | undefined): boolean {
  if (!url) return false;
  return (
    url.includes(AUTH_ENDPOINTS.login) ||
    url.includes(AUTH_ENDPOINTS.register) ||
    url.includes(AUTH_ENDPOINTS.refresh)
  );
}

async function refreshSession(): Promise<string> {
  const { refreshToken } = useAuthStore.getState();

  if (!refreshToken) {
    throw new Error("Sessão sem refresh token disponível.");
  }

  // Chamada crua via `axios` (não `apiClient`), para não passar pelos
  // interceptors acima e evitar recursão caso o próprio refresh retorne 401.
  const response = await axios.post<ApiEnvelope<RefreshResponseData>>(
    `${apiClient.defaults.baseURL ?? ""}${AUTH_ENDPOINTS.refresh}`,
    { refresh_token: refreshToken },
  );

  const newAccessToken = response.data.data.access_token;
  useAuthStore.getState().setAccessToken(newAccessToken);

  return newAccessToken;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;
    const isUnauthorized = error.response?.status === 401;

    const shouldAttemptRefresh =
      isUnauthorized &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthEndpoint(originalRequest.url);

    if (!shouldAttemptRefresh || !originalRequest) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      pendingRefresh ??= refreshSession().finally(() => {
        pendingRefresh = null;
      });
      const newAccessToken = await pendingRefresh;

      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      useAuthStore.getState().clearSession();

      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }

      return Promise.reject(refreshError);
    }
  },
);
