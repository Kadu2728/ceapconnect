/**
 * Contrato do Portal do Responsável (`GET/POST /guardian-portal/{token}`),
 * espelhando o backend. Acesso via link mágico — sem login, sem conta.
 */
export interface GuardianPortalView {
  candidate_first_name: string;
  training_date: string | null;
  training_location: string;
  training_confirmed_at: string | null;
  training_attended_at: string | null;
}
