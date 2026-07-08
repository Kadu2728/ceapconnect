/**
 * Indicadores institucionais do CEAP — Centro Educacional Assistencial
 * Profissionalizante (São Paulo/SP) — exibidos na Landing Page como prova de
 * confiança. Valores numéricos animam com contagem crescente; `display` cobre
 * o caso não-numérico.
 */
export interface Stat {
  /** Valor numérico para a animação de contagem (quando aplicável). */
  value?: number;
  /** Prefixo/sufixo do número (ex.: "+", "%"). */
  suffix?: string;
  /** Texto estático usado quando não há valor numérico. */
  display?: string;
  label: string;
}

export const STATS: Stat[] = [
  { value: 40, suffix: "", label: "Anos de história" },
  { value: 4, suffix: "", label: "Cursos técnicos gratuitos" },
  { display: "+10 mil", label: "Jovens transformados" },
  { value: 100, suffix: "%", label: "Gratuito, sempre" },
];
