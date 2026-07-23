"""Schemas Pydantic da feature de Recompensas (EPIC 13).

Contrato de:
- `GET  /api/v1/rewards`             → catálogo com nível + status por recompensa;
- `POST /api/v1/rewards/{id}/redeem` → resgate de uma recompensa desbloqueada.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.gamification import LevelInfo

# Status da recompensa para ESTE candidato:
# - locked    → condição de desbloqueio ainda não atingida;
# - available → desbloqueada e disponível para resgate;
# - redeemed  → resgatada, aguardando entrega da equipe;
# - fulfilled → entregue/confirmada pelo admin.
RewardStatus = Literal["locked", "available", "redeemed", "fulfilled"]

RewardUnlockType = Literal["level", "achievement"]


class RewardItem(BaseModel):
    """Uma recompensa do catálogo, já com o status do candidato."""

    id: uuid.UUID
    title: str
    description: str
    provider: str
    category: str
    icon: str
    featured: bool
    unlock_type: RewardUnlockType
    required_level: int | None
    # Texto pronto para UI (ex.: "Alcance o Nível 4" / "Desbloqueie a conquista 'X'").
    requirement_label: str
    status: RewardStatus
    redeemed_at: datetime | None
    fulfilled_at: datetime | None


class RewardSummary(BaseModel):
    """Resumo de progresso do candidato no catálogo de recompensas."""

    total: int
    unlocked: int  # condição atingida (available + redeemed + fulfilled)
    redeemed: int  # já resgatadas (redeemed + fulfilled)


class RewardListResponse(BaseModel):
    """Payload de `GET /api/v1/rewards`."""

    level: LevelInfo
    rewards: list[RewardItem]
    summary: RewardSummary


class RedeemRewardResponse(BaseModel):
    """Payload de `POST /api/v1/rewards/{id}/redeem`."""

    reward: RewardItem
