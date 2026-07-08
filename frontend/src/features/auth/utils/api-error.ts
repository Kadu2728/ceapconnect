import { isAxiosError } from "axios";

interface PydanticValidationError {
  msg: string;
}

interface KnownErrorBody {
  message?: string;
  detail?: string | PydanticValidationError[];
}

/**
 * Extrai uma mensagem de erro legível de qualquer formato retornado pela
 * API: o envelope padrão `{ message }` (API_GUIDELINES.md), o formato cru de
 * exceções do FastAPI (`{ detail: string }`) ou a lista de erros de
 * validação do Pydantic (`{ detail: [{ msg }] }`). Centralizar essa lógica
 * evita espalhar `try/catch` heurístico pelos hooks de cada feature.
 */
export function extractApiErrorMessage(error: unknown, fallback: string): string {
  if (!isAxiosError(error)) return fallback;

  if (!error.response) {
    return "Não foi possível conectar ao servidor. Verifique sua internet e tente novamente.";
  }

  const body = error.response.data as KnownErrorBody | undefined;
  const message = body?.message;
  const detail = body?.detail;

  if (typeof message === "string" && message.length > 0) {
    return message;
  }

  if (typeof detail === "string" && detail.length > 0) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const [firstError] = detail;
    if (firstError?.msg) return firstError.msg;
  }

  return fallback;
}

/** Status HTTP do erro, quando disponível — usado para diferenciar 401/409/422. */
export function getApiErrorStatus(error: unknown): number | undefined {
  return isAxiosError(error) ? error.response?.status : undefined;
}
