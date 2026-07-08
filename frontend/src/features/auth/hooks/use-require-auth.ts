"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuthStore } from "@/features/auth/store/auth-store";

/**
 * Guard client-side reutilizável para qualquer rota que exija autenticação
 * (Dashboard hoje; Missões, Conquistas, Eventos etc. na EPIC 03+).
 *
 * Aguarda `hasHydrated` antes de decidir redirecionar: sem isso, toda rota
 * protegida sofreria um "flash" de redirecionamento para `/login` no
 * primeiro render, já que a store começa vazia no client até o `persist`
 * carregar o `localStorage`.
 *
 * @returns `true` quando é seguro renderizar o conteúdo protegido.
 */
export function useRequireAuth(): boolean {
  const router = useRouter();
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const accessToken = useAuthStore((state) => state.accessToken);

  useEffect(() => {
    if (hasHydrated && !accessToken) {
      router.replace("/login");
    }
  }, [hasHydrated, accessToken, router]);

  return hasHydrated && Boolean(accessToken);
}
