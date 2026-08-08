import { apiClient } from "@/lib/axios";

import type {
  AnswerResult,
  AttemptHistory,
  FinishAttemptResult,
  StartAttemptResult,
} from "@/features/simulados/types/simulado.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da feature Simulados — única camada autorizada a falar com
 * `apiClient` neste domínio.
 */
const SIMULADOS_ENDPOINT = "/api/v1/simulados";

export async function startSimulado(): Promise<StartAttemptResult> {
  const { data } = await apiClient.post<ApiEnvelope<StartAttemptResult>>(
    `${SIMULADOS_ENDPOINT}/start`,
  );
  return data.data;
}

export async function answerQuestion(
  attemptId: string,
  questionId: string,
  selectedOptionKey: string,
): Promise<AnswerResult> {
  const { data } = await apiClient.post<ApiEnvelope<AnswerResult>>(
    `${SIMULADOS_ENDPOINT}/${attemptId}/answer`,
    { question_id: questionId, selected_option_key: selectedOptionKey },
  );
  return data.data;
}

export async function finishSimulado(attemptId: string): Promise<FinishAttemptResult> {
  const { data } = await apiClient.post<ApiEnvelope<FinishAttemptResult>>(
    `${SIMULADOS_ENDPOINT}/${attemptId}/finish`,
  );
  return data.data;
}

export async function fetchSimuladoHistory(): Promise<AttemptHistory> {
  const { data } = await apiClient.get<ApiEnvelope<AttemptHistory>>(
    `${SIMULADOS_ENDPOINT}/history`,
  );
  return data.data;
}
