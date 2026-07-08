import { useSyncExternalStore } from "react";

const subscribe = () => () => {};
const getSnapshot = () => true;
const getServerSnapshot = () => false;

/**
 * Retorna `true` somente após a hidratação no client.
 *
 * Usa `useSyncExternalStore` em vez de `useState` + `useEffect` porque essa
 * é a API pensada pelo React para diferenciar snapshot de server/client sem
 * disparar um setState síncrono dentro de um efeito (cascading render).
 */
export function useHasMounted(): boolean {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
