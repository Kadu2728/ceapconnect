import type { VideoProvider } from "@/features/learning/types/learning.types";

/**
 * O que o player precisa para reproduzir, já resolvido para o provedor.
 *
 * Único ponto do front que conhece provedores: trocar a hospedagem (CDN,
 * storage, plataforma de vídeo) amanhã significa acrescentar um `case` aqui —
 * nenhum componente de UI muda.
 */
export interface ResolvedVideoSource {
  kind: "native";
  src: string;
}

export function resolveVideoSource(
  provider: VideoProvider,
  ref: string,
): ResolvedVideoSource {
  switch (provider) {
    case "url":
      return { kind: "native", src: ref };
  }
}

/** `12 min` / `1 h 05 min` / `45 s` — para listagens, sem carregar o vídeo. */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds} s`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  if (hours === 0) return `${minutes} min`;
  return `${hours} h ${String(minutes).padStart(2, "0")} min`;
}

/** `07:00` / `1:02:30` — para "Continuar de …" e para o próprio player. */
export function formatTimestamp(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  const mmss = `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  return hours > 0 ? `${hours}:${mmss}` : mmss;
}
