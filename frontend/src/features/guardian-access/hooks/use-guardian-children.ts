"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchGuardianChildren } from "@/features/guardian-access/services/guardian-access.service";

export const GUARDIAN_CHILDREN_QUERY_KEY = ["guardian-children"] as const;

export function useGuardianChildren() {
  return useQuery({
    queryKey: GUARDIAN_CHILDREN_QUERY_KEY,
    queryFn: fetchGuardianChildren,
  });
}
