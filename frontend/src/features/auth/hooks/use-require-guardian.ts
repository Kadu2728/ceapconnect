"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useRequireAuth } from "@/features/auth/hooks/use-require-auth";
import { useAuthStore } from "@/features/auth/store/auth-store";

/**
 * Guard das páginas da Área do Responsável: sessão (`useRequireAuth`) +
 * papel `guardian`. Quem não é responsável vai para o Dashboard — o backend
 * também barra com 403 (defesa em profundidade; esconder a tela aqui é UX,
 * nunca segurança).
 *
 * Extraído quando a terceira página do responsável ia repetir o mesmo
 * `useEffect` — mesma disciplina de `useRequireAuth` para as páginas do
 * candidato.
 *
 * @returns `true` quando é seguro renderizar o conteúdo protegido.
 */
export function useRequireGuardian(): boolean {
  const router = useRouter();
  const isAuthenticated = useRequireAuth();
  const storedUser = useAuthStore((state) => state.user);
  const isGuardian = storedUser?.role === "guardian";

  useEffect(() => {
    if (isAuthenticated && storedUser && !isGuardian) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, storedUser, isGuardian, router]);

  return isAuthenticated && isGuardian;
}
