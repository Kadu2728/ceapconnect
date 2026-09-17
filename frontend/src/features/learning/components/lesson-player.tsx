"use client";

import { AlertCircle, Loader2, RotateCcw } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import type { VideoProvider } from "@/features/learning/types/learning.types";
import {
  formatTimestamp,
  resolveVideoSource,
} from "@/features/learning/utils/video-source";

interface LessonPlayerProps {
  provider: VideoProvider;
  videoRef: string;
  title: string;
  /** Posição de onde retomar; `0` começa do início. */
  resumeFromSeconds: number;
  onTimeUpdate: (positionSeconds: number) => void;
  onPause: () => void;
  onEnded: () => void;
}

type PlayerState = "idle" | "loading" | "ready" | "slow" | "error";

/** Acima disso sem o vídeo ficar pronto, avisamos que a conexão está lenta. */
const SLOW_CONNECTION_MS = 6_000;

/**
 * Player de videoaula — `<video>` nativo, zero biblioteca.
 *
 * Por que nativo: play/pause, volume, barra de progresso, fullscreen e
 * legendas já vêm do navegador, com o comportamento que o celular da pessoa
 * conhece (inclusive picture-in-picture e controle na tela de bloqueio). Uma
 * biblioteca de player pesaria 100–300 KB para reimplementar isso — no
 * público do CEAP, isso é franquia de dados e RAM.
 *
 * Baixo consumo, por construção:
 * - `preload="metadata"`: carrega só o cabeçalho (duração, dimensões) — o
 *   vídeo em si só baixa quando a pessoa dá play. Nunca autoplay.
 * - Um único `<video>` montado por vez; ao desmontar, `src` é liberado.
 * - A posição de retomada é aplicada uma vez, em `loadedmetadata`, sem
 *   provocar download antecipado.
 */
export function LessonPlayer({
  provider,
  videoRef,
  title,
  resumeFromSeconds,
  onTimeUpdate,
  onPause,
  onEnded,
}: LessonPlayerProps) {
  const source = resolveVideoSource(provider, videoRef);
  const videoElement = useRef<HTMLVideoElement>(null);
  const [state, setState] = useState<PlayerState>("idle");
  const [retryKey, setRetryKey] = useState(0);

  // Detecta conexão lenta: se o vídeo começou a carregar e não ficou pronto
  // dentro do limite, trocamos "carregando" por uma mensagem honesta — a
  // pessoa precisa saber que não travou.
  useEffect(() => {
    if (state !== "loading") return;
    const timer = window.setTimeout(() => setState("slow"), SLOW_CONNECTION_MS);
    return () => window.clearTimeout(timer);
  }, [state]);

  // Libera o buffer ao sair da aula — em aparelhos com pouca RAM, um vídeo
  // decodificado que ficou para trás é memória que a próxima tela não tem.
  useEffect(() => {
    const element = videoElement.current;
    return () => {
      if (element) {
        element.pause();
        element.removeAttribute("src");
        element.load();
      }
    };
  }, [retryKey]);

  const handleLoadedMetadata = () => {
    const element = videoElement.current;
    if (element && resumeFromSeconds > 0 && resumeFromSeconds < element.duration) {
      element.currentTime = resumeFromSeconds;
    }
  };

  const retry = () => {
    setState("idle");
    setRetryKey((key) => key + 1);
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="relative overflow-hidden rounded-2xl bg-black">
        <video
          key={retryKey}
          ref={videoElement}
          className="aspect-video w-full"
          controls
          playsInline
          preload="metadata"
          controlsList="nodownload"
          aria-label={`Videoaula: ${title}`}
          onLoadStart={() => setState("loading")}
          onLoadedMetadata={handleLoadedMetadata}
          onCanPlay={() => setState("ready")}
          onWaiting={() => setState("loading")}
          onPlaying={() => setState("ready")}
          onError={() => setState("error")}
          onTimeUpdate={(event) => onTimeUpdate(event.currentTarget.currentTime)}
          onPause={onPause}
          onEnded={onEnded}
        >
          <source src={source.src} />
          Seu navegador não consegue reproduzir este vídeo.
        </video>

        {state === "loading" || state === "slow" ? (
          <div
            role="status"
            aria-live="polite"
            className="pointer-events-none absolute inset-x-0 bottom-14 flex justify-center px-4"
          >
            <span className="inline-flex items-center gap-2 rounded-full bg-black/70 px-3 py-1.5 text-xs text-white">
              <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
              {state === "slow"
                ? "Sua conexão está lenta. Aguarde enquanto carregamos o conteúdo."
                : "Carregando aula…"}
            </span>
          </div>
        ) : null}

        {state === "error" ? (
          <div
            role="alert"
            className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black/85 px-6 text-center text-white"
          >
            <AlertCircle className="size-8 text-warning" aria-hidden="true" />
            <p className="text-sm">Não foi possível carregar esta aula.</p>
            <Button variant="outline" size="sm" onClick={retry} className="gap-2">
              <RotateCcw className="size-4" aria-hidden="true" />
              Tentar novamente
            </Button>
          </div>
        ) : null}
      </div>

      {resumeFromSeconds > 0 && state !== "error" ? (
        <p className="text-xs text-muted-foreground">
          Continuando de {formatTimestamp(resumeFromSeconds)}.
        </p>
      ) : null}
    </div>
  );
}
