"""Regra de negócio do consentimento do candidato ao vínculo do responsável
(RBAC do responsável — fase C).

Fecha o ciclo aberto na fase A: todo `GuardianCandidateLink` nasce `pending`
(sem coleta de data de nascimento em lugar nenhum do sistema, o backend
nunca decide maioridade sozinho — ver docstring do model), e é só aqui que
o candidato autoriza (`pending`/`revoked` → `granted`) ou revoga
(`granted` → `revoked`) o acesso de um responsável à própria jornada.
`GuardianScope` (`app.core.rbac`) já filtra por `AUTHORIZED_CONSENT_STATUSES`
— nenhuma mudança necessária ali, esta fase só dá ao candidato a alavanca
que decide esse estado.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.guardian_candidate_link import (
    CONSENT_GRANTED,
    CONSENT_REVOKED,
    GuardianCandidateLink,
)
from app.models.user import User
from app.repositories.guardian_candidate_link_repository import GuardianCandidateLinkRepository
from app.repositories.user_repository import UserRepository
from app.schemas.guardian_consent import GuardianLinkConsentItem, GuardianLinkConsentListResponse
from app.services.candidate_profile_service import get_profile_or_raise


async def list_links(db: AsyncSession, user: User) -> GuardianLinkConsentListResponse:
    """Todos os responsáveis vinculados a este candidato, qualquer que seja o status."""
    profile = await get_profile_or_raise(db, user)
    links = await GuardianCandidateLinkRepository(db).list_for_candidate(profile.id)
    if not links:
        return GuardianLinkConsentListResponse(links=[])

    guardian_users = {
        guardian_user.id: guardian_user
        for guardian_user in await UserRepository(db).get_by_ids(
            [link.guardian_user_id for link in links]
        )
    }

    items = [
        _to_item(link, guardian_users[link.guardian_user_id])
        for link in links
        if link.guardian_user_id in guardian_users
    ]
    return GuardianLinkConsentListResponse(links=items)


async def grant_consent(
    db: AsyncSession, user: User, link_id: uuid.UUID
) -> GuardianLinkConsentItem:
    """Autoriza o vínculo — o responsável passa a ver a jornada a partir daqui."""
    link = await _get_own_link_or_raise(db, user, link_id)
    link.consent_status = CONSENT_GRANTED
    await db.commit()
    return await _to_item_with_guardian(db, link)


async def revoke_consent(
    db: AsyncSession, user: User, link_id: uuid.UUID
) -> GuardianLinkConsentItem:
    """Revoga um vínculo já autorizado — o responsável perde acesso imediatamente."""
    link = await _get_own_link_or_raise(db, user, link_id)
    link.consent_status = CONSENT_REVOKED
    await db.commit()
    return await _to_item_with_guardian(db, link)


async def _get_own_link_or_raise(
    db: AsyncSession, user: User, link_id: uuid.UUID
) -> GuardianCandidateLink:
    """Resolve o vínculo garantindo que pertence ao candidato autenticado.

    Um `link_id` de outro candidato levanta o mesmo `NotFoundException` de um
    id inexistente — nunca revela que o vínculo existe, só não é seu.
    """
    profile = await get_profile_or_raise(db, user)
    link = await GuardianCandidateLinkRepository(db).get_by_id(link_id)
    if link is None or link.candidate_profile_id != profile.id:
        raise NotFoundException("Vínculo não encontrado.")
    return link


async def _to_item_with_guardian(
    db: AsyncSession, link: GuardianCandidateLink
) -> GuardianLinkConsentItem:
    guardian_user = await UserRepository(db).get_by_id(link.guardian_user_id)
    if guardian_user is None:
        raise NotFoundException("Vínculo não encontrado.")
    return _to_item(link, guardian_user)


def _to_item(link: GuardianCandidateLink, guardian_user: User) -> GuardianLinkConsentItem:
    return GuardianLinkConsentItem(
        id=link.id,
        guardian_name=guardian_user.name,
        guardian_email=guardian_user.email,
        consent_status=link.consent_status,
        created_at=link.created_at,
    )
