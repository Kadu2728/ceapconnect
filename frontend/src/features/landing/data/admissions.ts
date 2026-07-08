import { PencilRuler, UserPlus, Users, type LucideIcon } from "lucide-react";

/**
 * Etapas reais do processo seletivo do CEAP — Centro Educacional Assistencial
 * Profissionalizante (fonte: ceappedreira.org.br). É gratuito e composto por
 * inscrição, prova e entrevista. O CEAP Connect acompanha o candidato em cada
 * uma dessas etapas.
 */
export interface SelectionStep {
  title: string;
  description: string;
  icon: LucideIcon;
}

export const SELECTION_STEPS: SelectionStep[] = [
  {
    title: "Inscrição online",
    description:
      "Cadastre-se gratuitamente pelo site e garanta sua vaga na seleção — sem nenhum custo.",
    icon: UserPlus,
  },
  {
    title: "Prova",
    description:
      "Prova de Português e Matemática: 20 questões objetivas em cerca de 1 hora.",
    icon: PencilRuler,
  },
  {
    title: "Entrevista",
    description: "Entrevista presencial com a presença do seu pai, mãe ou responsável.",
    icon: Users,
  },
];
