"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef } from "react";

import { toast } from "@/components/feedback/toast/toast-store";
import { COURSE_OVERVIEW_QUERY_KEY } from "@/features/learning/hooks/use-course-overview";
import { LESSON_QUERY_KEY } from "@/features/learning/hooks/use-lesson";
import { updateLessonProgress } from "@/features/learning/services/learning.service";

/**
 * Intervalo mínimo entre gravações de posição durante a reprodução.
 * `timeupdate` dispara ~4×/s; gravar cada um seria uma request a cada 250ms
 * numa conexão móvel. 10s é curto o bastante para o "continuar de" ser
 * preciso e longo o bastante para não pesar no plano de dados.
 */
const SYNC_INTERVAL_MS = 10_000;

/**
 * Sincroniza a posição assistida com o backend, com a cadência decidida
 * aqui (não no player, que só reporta o que o `<video>` diz).
 *
 * - `report(position)` — chamar em todo `timeupdate`; grava no máximo a cada
 *   `SYNC_INTERVAL_MS`.
 * - `flush()` — grava **agora** a última posição conhecida; chamar ao pausar,
 *   ao terminar e ao sair da página, para não perder os últimos segundos.
 *
 * Ao cruzar o limiar de conclusão, invalida a visão geral do curso — o
 * dashboard do curso atualiza sem reload, como o brief pede.
 */
export function useLessonProgress(lessonId: string, courseSlug: string) {
  const queryClient = useQueryClient();
  const lastSentAtRef = useRef(0);
  const lastPositionRef = useRef(0);
  const lastSentPositionRef = useRef(-1);

  const mutation = useMutation({
    mutationFn: (positionSeconds: number) =>
      updateLessonProgress(lessonId, positionSeconds),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: COURSE_OVERVIEW_QUERY_KEY(courseSlug) });
      queryClient.invalidateQueries({ queryKey: LESSON_QUERY_KEY(lessonId) });
      if (result.just_completed) {
        toast.success("Aula concluída!", {
          description: "Seu progresso no curso foi atualizado.",
        });
      }
    },
    // Silencioso de propósito: uma falha de sincronização não pode
    // interromper o vídeo. Libera a deduplicação para a próxima gravação
    // (mesmo na mesma posição) tentar de novo — senão um flush que falhou ao
    // pausar aos 5s nunca seria repetido ao fechar a aba nos mesmos 5s.
    onError: () => {
      lastSentPositionRef.current = -1;
    },
  });

  const { mutate } = mutation;

  // Grava só se a posição inteira mudou desde a última gravação. O `<video>`
  // dispara `pause` e `ended` em sequência ao terminar — sem isso, dois
  // flushes idênticos saem quase ao mesmo tempo: uma request a mais no plano
  // de dados e uma corrida no backend (que ele resolve, mas não precisa).
  const send = useCallback(
    (positionSeconds: number) => {
      const whole = Math.floor(positionSeconds);
      if (whole === lastSentPositionRef.current) return;
      lastSentPositionRef.current = whole;
      lastSentAtRef.current = Date.now();
      mutate(whole);
    },
    [mutate],
  );

  const report = useCallback(
    (positionSeconds: number) => {
      lastPositionRef.current = positionSeconds;
      if (Date.now() - lastSentAtRef.current >= SYNC_INTERVAL_MS) {
        send(positionSeconds);
      }
    },
    [send],
  );

  const flush = useCallback(() => {
    if (lastPositionRef.current > 0) send(lastPositionRef.current);
  }, [send]);

  // Sair da página (voltar, fechar a aba, trocar de app no celular) grava a
  // última posição — sem isso, os últimos segundos antes de sair se perdem.
  useEffect(() => {
    const onHide = () => {
      if (document.visibilityState === "hidden") flush();
    };
    document.addEventListener("visibilitychange", onHide);
    return () => {
      document.removeEventListener("visibilitychange", onHide);
      flush();
    };
  }, [flush]);

  return { report, flush };
}
