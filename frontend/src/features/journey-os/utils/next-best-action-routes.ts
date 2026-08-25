import { FileText, MessageCircleHeart, NotebookPen, Route } from "lucide-react";

import type { NextBestActionKey } from "@/features/journey-os/types/journey-os.types";

/**
 * Para onde o clique no card de Next Best Action leva, e qual ícone
 * representa a ação — centralizado aqui para o card e o Modo Resgate
 * (que reaproveita a mesma recomendação) nunca divergirem.
 *
 * `remind_guardian` vai para `/perfil`: é lá que já existe o fluxo real de
 * avisar o responsável (WhatsApp/e-mail — `guardian-notice-card.tsx`), não
 * uma tela nova.
 */
export const NEXT_BEST_ACTION_ROUTES: Record<NextBestActionKey, string> = {
  upload_documents: "/documentos",
  remind_guardian: "/perfil",
  prepare_for_exam: "/simulados",
  resume_journey: "/dashboard",
};

export const NEXT_BEST_ACTION_ICONS: Record<NextBestActionKey, typeof FileText> = {
  upload_documents: FileText,
  remind_guardian: MessageCircleHeart,
  prepare_for_exam: NotebookPen,
  resume_journey: Route,
};
