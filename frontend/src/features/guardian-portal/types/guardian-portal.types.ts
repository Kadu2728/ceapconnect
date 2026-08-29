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
  /** `true` quando este link já foi usado para criar uma conta de responsável (fase B). */
  account_already_active: boolean;
}

/** Corpo de `POST /guardian-portal/{token}/activate` — mesmos campos do cadastro de candidato. */
export interface GuardianAccountActivationRequest {
  name: string;
  email: string;
  cpf: string;
  phone: string;
  password: string;
  password_confirmation: string;
}
