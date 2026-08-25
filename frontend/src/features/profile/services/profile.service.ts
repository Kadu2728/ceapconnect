import { apiClient } from "@/lib/axios";

import type {
  GuardianEmailNoticeResult,
  GuardianTrainingEmailNoticeResult,
  Profile,
  ProfileUpdateInput,
} from "@/features/profile/types/profile.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service da Tela de Perfil — única camada autorizada a falar com `apiClient`
 * neste domínio.
 */
const PROFILE_ENDPOINT = "/api/v1/profile";

export async function fetchProfile(): Promise<Profile> {
  const { data } = await apiClient.get<ApiEnvelope<Profile>>(PROFILE_ENDPOINT);
  return data.data;
}

export async function updateProfile(input: ProfileUpdateInput): Promise<Profile> {
  const { data } = await apiClient.patch<ApiEnvelope<Profile>>(PROFILE_ENDPOINT, input);
  return data.data;
}

export async function notifyGuardianByEmail(): Promise<GuardianEmailNoticeResult> {
  const { data } = await apiClient.post<ApiEnvelope<GuardianEmailNoticeResult>>(
    `${PROFILE_ENDPOINT}/guardian/notify-email`,
  );
  return data.data;
}

export async function notifyGuardianTrainingByEmail(): Promise<GuardianTrainingEmailNoticeResult> {
  const { data } = await apiClient.post<ApiEnvelope<GuardianTrainingEmailNoticeResult>>(
    `${PROFILE_ENDPOINT}/guardian/notify-training`,
  );
  return data.data;
}
