import { create } from "zustand";

export type ToastVariant = "success" | "error" | "info";

export interface ToastItem {
  id: string;
  variant: ToastVariant;
  title: string;
  description?: string;
}

interface ToastState {
  toasts: ToastItem[];
  show: (toast: Omit<ToastItem, "id">) => void;
  dismiss: (id: string) => void;
}

const TOAST_DURATION_MS = 5000;

/** Store efêmera (não persistida) da fila de toasts ativos na tela. */
export const useToastStore = create<ToastState>((set, get) => ({
  toasts: [],
  show: (item) => {
    const id = crypto.randomUUID();
    set((state) => ({ toasts: [...state.toasts, { ...item, id }] }));

    setTimeout(() => {
      get().dismiss(id);
    }, TOAST_DURATION_MS);
  },
  dismiss: (id) => {
    set((state) => ({ toasts: state.toasts.filter((item) => item.id !== id) }));
  },
}));

interface ToastOptions {
  description?: string;
}

/**
 * API pública de disparo de toasts — utilizável em qualquer lugar (handlers
 * de mutation, services etc.) sem precisar de um hook React, inspirada na
 * API do `sonner`. Implementada com Zustand (já presente no stack) em vez
 * de adicionar uma biblioteca de terceiros só para isso.
 *
 * O viewport que efetivamente renderiza os toasts é `<Toaster />`
 * (montado uma única vez em `AppProviders`).
 */
export const toast = {
  success: (title: string, options?: ToastOptions) =>
    useToastStore
      .getState()
      .show({ variant: "success", title, description: options?.description }),
  error: (title: string, options?: ToastOptions) =>
    useToastStore
      .getState()
      .show({ variant: "error", title, description: options?.description }),
};
