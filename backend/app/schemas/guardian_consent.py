"""Schemas do consentimento do candidato ao vínculo do responsável (RBAC do
responsável — fase C).

Contrato de:
- `GET  /api/v1/profile/guardian-links`               → responsáveis que pediram vínculo;
- `POST /api/v1/profile/guardian-links/{id}/consent`  → autoriza um vínculo;
- `POST /api/v1/profile/guardian-links/{id}/revoke`   → revoga um vínculo já autorizado.

Todo vínculo nasce `pending` (ver `app.models.guardian_candidate_link` —
não há coleta de data de nascimento em lugar nenhum do sistema, então o
backend nunca decide maioridade sozinho): é o candidato, sempre, quem
autoriza ou revoga — nunca automático.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.guardian_candidate_link import ConsentStatus


class GuardianLinkConsentItem(BaseModel):
    """Um vínculo de responsável, da perspectiva do candidato."""

    id: uuid.UUID
    guardian_name: str
    guardian_email: str
    consent_status: ConsentStatus
    created_at: datetime


class GuardianLinkConsentListResponse(BaseModel):
    links: list[GuardianLinkConsentItem]
