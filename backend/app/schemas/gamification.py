"""Schemas Pydantic de gamificação compartilhados (EPIC 13).

`LevelInfo` é a projeção de API de `app.core.gamification.LevelProgress`.
Vive aqui — e não em `dashboard.py`/`reward.py` — porque é consumido por
ambos (Dashboard e Recompensas), mantendo uma fonte única do contrato de nível.
"""

from pydantic import BaseModel


class LevelInfo(BaseModel):
    """Nível atual do candidato e progresso rumo ao próximo."""

    level: int
    name: str
    xp_total: int
    current_level_xp: int
    next_level_xp: int | None
    xp_into_level: int
    xp_to_next: int | None
    progress_percentage: int
    is_max_level: bool
