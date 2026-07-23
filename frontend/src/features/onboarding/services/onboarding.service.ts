import { apiClient } from "@/lib/axios";

/**
 * Service do onboarding — marca a tela de boas-vindas como concluída.
 */
export async function completeOnboarding(): Promise<void> {
  await apiClient.post("/api/v1/onboarding/complete");
}
