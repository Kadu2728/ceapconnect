import { Briefcase, Clapperboard, Code2, Network, type LucideIcon } from "lucide-react";

/**
 * Cursos técnicos gratuitos oferecidos pelo CEAP — Centro Educacional
 * Assistencial Profissionalizante (fonte: ceappedreira.org.br). Exibidos na
 * Landing para dar concretude ao processo seletivo que o CEAP Connect
 * acompanha.
 */
export interface Course {
  name: string;
  description: string;
  icon: LucideIcon;
}

export const COURSES: Course[] = [
  {
    name: "Administração",
    description: "Gestão, liderança, análise de dados e empreendedorismo.",
    icon: Briefcase,
  },
  {
    name: "Informática",
    description: "Programação, desenvolvimento web e mobile, nuvem e IA.",
    icon: Code2,
  },
  {
    name: "Redes de Computadores",
    description: "Servidores, cibersegurança e certificações CISCO.",
    icon: Network,
  },
  {
    name: "Cinema e Audiovisual",
    description: "Captação, edição, roteiro e produção de conteúdo.",
    icon: Clapperboard,
  },
];
