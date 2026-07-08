/**
 * Etapas da jornada do candidato no CEAP Connect (USER_FLOW.md), apresentadas
 * na Landing Page como uma trilha numerada. A jornada real, dinâmica e por
 * candidato, vive no Dashboard.
 */
export interface JourneyStage {
  title: string;
  description: string;
}

export const JOURNEY_STAGES: JourneyStage[] = [
  {
    title: "Cadastro",
    description: "Crie sua conta em minutos e entre oficialmente na sua jornada.",
  },
  {
    title: "Boas-vindas",
    description: "Conheça missões, conquistas e sua trilha em um onboarding rápido.",
  },
  {
    title: "Missões & XP",
    description: "Complete ações guiadas, ganhe experiência e acompanhe seu progresso.",
  },
  {
    title: "Eventos & Preparação",
    description: "Participe de eventos e chegue preparado para a prova e a entrevista.",
  },
  {
    title: "Prova & Entrevista",
    description: "Vá com confiança: datas, local e lembretes organizados para você.",
  },
  {
    title: "Resultado",
    description: "Acompanhe seu resultado e os próximos passos, tudo em um só lugar.",
  },
];
