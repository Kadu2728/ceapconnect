import { apiClient } from "@/lib/axios";

import type { DashboardData } from "@/features/dashboard/types/dashboard.types";
import type { ApiEnvelope } from "@/types/api";

/**
 * Service do Dashboard (EPIC 03) — única camada autorizada a chamar
 * `apiClient` para este domínio (ARCHITECTURE.md: "toda regra de negócio
 * deve permanecer fora da interface"). Hooks consomem esta função;
 * componentes nunca importam `apiClient` diretamente.
 */
const DASHBOARD_ENDPOINT = "/api/v1/dashboard";

export async function fetchDashboard(): Promise<DashboardData> {
  const { data } = await apiClient.get<ApiEnvelope<DashboardData>>(DASHBOARD_ENDPOINT);
  return data.data;
}
