"""Aviso ao responsável sobre a entrevista e a formação (EPIC 17 + item 5 do backlog).

Candidatos são menores de idade (14-18 anos) e o responsável tem duas etapas
obrigatórias no processo seletivo do CEAP — a formação e a entrevista — mas
não tem conta no app. Esta feature dá ao candidato um jeito real de avisá-lo:
e-mail (via API do Resend, com o mesmo racional de degradação graciosa do
assistente de IA — EPIC 11) e um link de WhatsApp pré-preenchido, que não
depende de nenhuma integração paga (é o próprio celular do candidato
enviando). O aviso da formação também inclui o link do Portal do Responsável
(`app.services.guardian_portal_service`) — o único jeito do responsável
confirmar presença sem precisar de conta.

Degradação graciosa: sem `RESEND_API_KEY`, o e-mail simplesmente não é
enviado — o endpoint responde com `sent=False` e uma mensagem clara, sem
quebrar a tela. O link de WhatsApp nunca depende dessa chave.
"""

import logging
from datetime import date
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.models.candidate_profile import CandidateProfile
from app.models.guardian import Guardian
from app.models.user import User

logger = logging.getLogger("ceap_connect.guardian_notice")

_RESEND_URL = "https://api.resend.com/emails"

_NOT_CONFIGURED_MESSAGE = (
    "O envio de e-mail ainda não foi ativado por aqui. Use o link de WhatsApp "
    "para avisar seu responsável enquanto isso."
)
_NO_GUARDIAN_EMAIL_MESSAGE = "Cadastre o e-mail do seu responsável antes de enviar o aviso."
_SEND_ERROR_MESSAGE = "Não foi possível enviar o e-mail agora. Tente novamente em instantes."
_SENT_MESSAGE = "E-mail enviado para o responsável com sucesso."


def is_configured() -> bool:
    """Indica se a chave da API do Resend está configurada."""
    return bool(settings.resend_api_key.strip())


def build_whatsapp_link(
    *, candidate_name: str, profile: CandidateProfile, guardian: Guardian | None
) -> str:
    """Monta um link `wa.me` com a mensagem já preenchida, na voz do candidato.

    Sem custo e sem integração: abre o WhatsApp do próprio celular do
    candidato com a mensagem pronta para o responsável. Se o telefone do
    responsável não estiver cadastrado, omite o número — o WhatsApp abre o
    seletor de contatos em vez de um destinatário fixo.
    """
    message = _build_message(candidate_name=candidate_name, profile=profile)
    encoded_message = quote(message)
    if guardian is not None and guardian.phone:
        return f"https://wa.me/55{guardian.phone}?text={encoded_message}"
    return f"https://wa.me/?text={encoded_message}"


async def send_guardian_email(
    *, user: User, profile: CandidateProfile, guardian: Guardian | None
) -> tuple[bool, str]:
    """Envia o e-mail de aviso ao responsável principal via Resend.

    Retorna `(sent, message)` — nunca levanta exceção por falha de rede/API:
    uma falha no envio não deve derrubar a tela de Perfil, só informar o
    candidato para tentar de novo (ou usar o WhatsApp).
    """
    if guardian is None or not guardian.email:
        return False, _NO_GUARDIAN_EMAIL_MESSAGE
    if not is_configured():
        return False, _NOT_CONFIGURED_MESSAGE

    subject = f"Entrevista do processo seletivo do CEAP — {user.name}"
    html = _build_email_html(candidate_name=user.name, profile=profile)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                _RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": f"CEAP Connect <{settings.resend_from_email}>",
                    "to": [guardian.email],
                    "subject": subject,
                    "html": html,
                },
            )
            if response.status_code >= 400:
                logger.error("Resend %s: %s", response.status_code, response.text[:600])
                return False, _SEND_ERROR_MESSAGE
    except httpx.HTTPError:
        logger.exception("Falha ao enviar e-mail de aviso ao responsável (Resend)")
        return False, _SEND_ERROR_MESSAGE

    return True, _SENT_MESSAGE


def build_confirmation_url(guardian: Guardian) -> str:
    """Link absoluto do Portal do Responsável — o próprio link mágico."""
    return f"{settings.frontend_url}/responsavel/{guardian.confirmation_token}"


def build_training_whatsapp_link(
    *, candidate_name: str, training_date: date | None, guardian: Guardian
) -> str:
    """Mesmo padrão de `build_whatsapp_link`, mas para a formação obrigatória
    — inclui o link de confirmação, já que essa é a etapa autoconfirmável."""
    message = _build_training_message(
        candidate_name=candidate_name, training_date=training_date, guardian=guardian
    )
    encoded_message = quote(message)
    if guardian.phone:
        return f"https://wa.me/55{guardian.phone}?text={encoded_message}"
    return f"https://wa.me/?text={encoded_message}"


async def send_training_notice_email(
    *, user: User, training_date: date | None, guardian: Guardian | None
) -> tuple[bool, str]:
    """Envia o e-mail de aviso da formação obrigatória, com o link de confirmação."""
    if guardian is None or not guardian.email:
        return False, _NO_GUARDIAN_EMAIL_MESSAGE
    if not is_configured():
        return False, _NOT_CONFIGURED_MESSAGE

    subject = f"Formação obrigatória do processo seletivo do CEAP — {user.name}"
    html = _build_training_email_html(
        candidate_name=user.name, training_date=training_date, guardian=guardian
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                _RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": f"CEAP Connect <{settings.resend_from_email}>",
                    "to": [guardian.email],
                    "subject": subject,
                    "html": html,
                },
            )
            if response.status_code >= 400:
                logger.error("Resend %s: %s", response.status_code, response.text[:600])
                return False, _SEND_ERROR_MESSAGE
    except httpx.HTTPError:
        logger.exception("Falha ao enviar e-mail de aviso da formação ao responsável (Resend)")
        return False, _SEND_ERROR_MESSAGE

    return True, _SENT_MESSAGE


def _build_training_message(
    *, candidate_name: str, training_date: date | None, guardian: Guardian
) -> str:
    date_label = _format_training_date(training_date)
    confirmation_url = build_confirmation_url(guardian)
    return (
        f"Oi! Aqui é o(a) {candidate_name}. A formação obrigatória do processo "
        f"seletivo do CEAP foi marcada para {date_label}, na "
        f"{settings.interview_location}. Você pode confirmar presença aqui: "
        f"{confirmation_url} 💚"
    )


def _build_training_email_html(
    *, candidate_name: str, training_date: date | None, guardian: Guardian
) -> str:
    date_label = _format_training_date(training_date)
    confirmation_url = build_confirmation_url(guardian)
    return (
        f"<p>Olá!</p>"
        f"<p><strong>{candidate_name}</strong> está no processo seletivo do CEAP "
        "(Centro Educacional Assistencial Profissionalizante) e a formação "
        "obrigatória do responsável está chegando.</p>"
        f"<p><strong>Data:</strong> {date_label}<br>"
        f"<strong>Local:</strong> {settings.interview_location}</p>"
        "<p>A participação do responsável é uma etapa obrigatória do processo, que é "
        "100% gratuito — sem ela, o candidato perde a vaga.</p>"
        f'<p><a href="{confirmation_url}">Confirmar presença</a></p>'
        "<p>Qualquer dúvida, entre em contato com a secretaria do CEAP.</p>"
    )


def _format_training_date(training_date: date | None) -> str:
    if training_date is None:
        return "em breve (data a confirmar)"
    return training_date.strftime("%d/%m/%Y")


def _build_message(*, candidate_name: str, profile: CandidateProfile) -> str:
    """Mensagem em texto puro (usada no link de WhatsApp), na 1ª pessoa do candidato."""
    date_label = _format_date(profile)
    return (
        f"Oi! Aqui é o(a) {candidate_name}. Minha entrevista do processo seletivo do "
        f"CEAP foi marcada para {date_label}, na {settings.interview_location}. "
        "Você pode vir comigo? 💚"
    )


def _build_email_html(*, candidate_name: str, profile: CandidateProfile) -> str:
    """E-mail simples em HTML com os dados da entrevista."""
    date_label = _format_date(profile)
    return (
        f"<p>Olá!</p>"
        f"<p><strong>{candidate_name}</strong> está no processo seletivo do CEAP "
        "(Centro Educacional Assistencial Profissionalizante) e a próxima etapa é a "
        "entrevista com o responsável.</p>"
        f"<p><strong>Data:</strong> {date_label}<br>"
        f"<strong>Local:</strong> {settings.interview_location}</p>"
        "<p>A participação do responsável é uma etapa obrigatória do processo, que é "
        "100% gratuito. Qualquer dúvida, entre em contato com a secretaria do CEAP.</p>"
    )


def _format_date(profile: CandidateProfile) -> str:
    if profile.interview_date is None:
        return "em breve (data a confirmar)"
    return profile.interview_date.strftime("%d/%m/%Y")
