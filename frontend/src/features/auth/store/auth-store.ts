import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import type { AuthUser } from "@/features/auth/types/auth.types";

interface AuthSession {
  accessToken: string;
  refreshToken: string;
  user: AuthUser;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  /** `true` somente após a store terminar de reidratar do `localStorage`. */
  hasHydrated: boolean;
}

interface AuthActions {
  setSession: (session: AuthSession) => void;
  setAccessToken: (accessToken: string) => void;
  clearSession: () => void;
  setHasHydrated: (value: boolean) => void;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  user: null,
  hasHydrated: false,
};

/**
 * Store global de sessão de autenticação.
 *
 * Persistida em `localStorage` (middleware `persist`) para sobreviver a
 * reloads — o candidato não deve perder a sessão ao atualizar a página.
 *
 * `skipHydration: true` é obrigatório aqui: sem essa opção, o `persist`
 * tentaria ler `localStorage` de forma síncrona no momento em que o módulo é
 * avaliado, o que quebra em SSR (Next.js renderiza Client Components uma
 * vez no servidor, onde `localStorage` não existe). A reidratação real é
 * disparada manualmente no client, uma única vez, em `AppProviders`.
 */
export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      ...initialState,
      setSession: ({ accessToken, refreshToken, user }) =>
        set({ accessToken, refreshToken, user }),
      setAccessToken: (accessToken) => set({ accessToken }),
      clearSession: () => set({ ...initialState, hasHydrated: true }),
      setHasHydrated: (value) => set({ hasHydrated: value }),
    }),
    {
      name: "ceap-connect-auth",
      storage: createJSONStorage(() => localStorage),
      skipHydration: true,
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    },
  ),
);
