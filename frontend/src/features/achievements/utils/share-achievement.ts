import type { Achievement } from "@/features/achievements/types/achievement.types";

/**
 * Link usado no compartilhamento: sempre o site público do CEAP, **nunca** uma
 * URL pessoal do candidato.
 *
 * Decisão deliberada de privacidade: o público são adolescentes de 14 a 18 anos
 * em situação de vulnerabilidade — expor nome, progresso ou perfil numa página
 * pública indexável seria um risco real, não uma feature. O orgulho da conquista
 * é compartilhado; os dados dele, não.
 */
const PUBLIC_SITE_URL = "https://ceappedreira.org.br";

export type ShareResult = "shared" | "copied" | "cancelled";

function buildShareText(achievement: Achievement): string {
  return `Desbloqueei a conquista "${achievement.name}" no CEAP Connect! 🏆 Estou no processo seletivo do CEAP — escola técnica gratuita.`;
}

/**
 * Compartilha uma conquista usando a Web Share API (nativa no celular, que é
 * onde esse público está) e cai para a área de transferência no desktop.
 * Sem nenhuma dependência nova e sem geração de imagem — texto + link já
 * entregam o valor com custo zero de bundle.
 */
export async function shareAchievement(achievement: Achievement): Promise<ShareResult> {
  const text = buildShareText(achievement);

  if (typeof navigator !== "undefined" && "share" in navigator) {
    try {
      await navigator.share({ title: "CEAP Connect", text, url: PUBLIC_SITE_URL });
      return "shared";
    } catch (error) {
      // O usuário fechar a folha de compartilhamento não é um erro a reportar.
      if (error instanceof DOMException && error.name === "AbortError")
        return "cancelled";
      // Qualquer outra falha (ex.: permissão negada) cai para a cópia abaixo.
    }
  }

  await navigator.clipboard.writeText(`${text} ${PUBLIC_SITE_URL}`);
  return "copied";
}
