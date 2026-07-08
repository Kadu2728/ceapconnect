"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { ThemeProvider } from "next-themes";
import { useEffect, useState, type ReactNode } from "react";

import { Toaster } from "@/components/feedback/toast/toaster";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { createQueryClient } from "@/lib/query-client";

interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Reúne todos os providers globais da aplicação (tema, cache de dados,
 * toasts, sessão de autenticação).
 *
 * Isolado como Client Component para manter o `RootLayout` como Server
 * Component, conforme FRONTEND_GUIDELINES.md ("Client Components apenas
 * quando necessário").
 */
export function AppProviders({ children }: AppProvidersProps) {
  const [queryClient] = useState(createQueryClient);

  useEffect(() => {
    // Reidratação manual e única da store de auth — ver comentário em
    // `features/auth/store/auth-store.ts` sobre por que `skipHydration` é
    // necessário aqui (evitar acesso a `localStorage` durante o SSR).
    void useAuthStore.persist.rehydrate();
  }, []);

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <QueryClientProvider client={queryClient}>
        {children}
        <Toaster />
        {process.env.NODE_ENV === "development" && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </ThemeProvider>
  );
}
