import { apiClient } from "@/lib/axios";

import { AUTH_ENDPOINTS } from "@/features/auth/constants";
import type {
  ApiEnvelope,
  CurrentUserResponseData,
  LoginRequest,
  LoginResponseData,
  RefreshResponseData,
  RegisterRequest,
  RegisterResponseData,
} from "@/features/auth/types/auth.types";

/**
 * Services de autenticação — única camada autorizada a chamar `apiClient`
 * para o domínio de auth (ARCHITECTURE.md: "toda regra de negócio deve
 * permanecer fora da interface"). Hooks consomem estas funções; componentes
 * nunca importam `apiClient` diretamente.
 */

export async function registerUser(
  payload: RegisterRequest,
): Promise<RegisterResponseData> {
  const { data } = await apiClient.post<ApiEnvelope<RegisterResponseData>>(
    AUTH_ENDPOINTS.register,
    payload,
  );
  return data.data;
}

export async function loginUser(payload: LoginRequest): Promise<LoginResponseData> {
  const { data } = await apiClient.post<ApiEnvelope<LoginResponseData>>(
    AUTH_ENDPOINTS.login,
    payload,
  );
  return data.data;
}

export async function refreshAccessToken(
  refreshToken: string,
): Promise<RefreshResponseData> {
  const { data } = await apiClient.post<ApiEnvelope<RefreshResponseData>>(
    AUTH_ENDPOINTS.refresh,
    {
      refresh_token: refreshToken,
    },
  );
  return data.data;
}

export async function fetchCurrentUser(): Promise<CurrentUserResponseData> {
  const { data } = await apiClient.get<ApiEnvelope<CurrentUserResponseData>>(
    AUTH_ENDPOINTS.me,
  );
  return data.data;
}
