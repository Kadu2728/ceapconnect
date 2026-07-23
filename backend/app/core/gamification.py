"""Regras de progressão por nível (gamificação — EPIC 13).

Camada de domínio **pura** (sem I/O): converte o XP acumulado do candidato numa
faixa de nível com rótulo, limites e progresso para o próximo nível. Consumida
pelo Dashboard e pela feature de Recompensas para exibir a progressão de forma
legível ("Nível 3 · Construtor — faltam 120 XP para o próximo nível").

Os limiares são um **catálogo de domínio, não schema**: ajustar a curva de XP
não exige migration. Mantê-los aqui — e não no banco — deixa o cálculo
determinístico, testável e sem custo de query a cada Dashboard.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LevelTier:
    """Uma faixa de nível: número, rótulo e XP mínimo para alcançá-la."""

    level: int
    name: str
    min_xp: int


# Curva progressiva: cada faixa exige mais que a anterior (esforço crescente,
# recompensa mais rara conforme sobe). Editável sem migration.
LEVEL_TIERS: tuple[LevelTier, ...] = (
    LevelTier(1, "Iniciante", 0),
    LevelTier(2, "Explorador", 100),
    LevelTier(3, "Construtor", 250),
    LevelTier(4, "Estrategista", 500),
    LevelTier(5, "Especialista", 850),
    LevelTier(6, "Mestre CEAP", 1300),
)


@dataclass(frozen=True)
class LevelProgress:
    """Progressão de nível já calculada para um XP específico."""

    level: int
    name: str
    xp_total: int
    current_level_xp: int  # limiar de entrada do nível atual
    next_level_xp: int | None  # limiar do próximo nível (None no nível máximo)
    xp_into_level: int  # XP acumulado dentro do nível atual
    xp_to_next: int | None  # XP faltando para o próximo (None no nível máximo)
    progress_percentage: int  # 0..100 dentro do nível atual (100 no máximo)
    is_max_level: bool


def resolve_level(xp_total: int) -> LevelProgress:
    """Converte um XP total na faixa de nível correspondente e seu progresso.

    Determinístico e defensivo: XP negativo é tratado como 0; no nível máximo,
    o progresso satura em 100% (não há "próximo nível").
    """
    xp = max(xp_total, 0)

    current = LEVEL_TIERS[0]
    upcoming: LevelTier | None = None
    for tier in LEVEL_TIERS:
        if xp >= tier.min_xp:
            current = tier
        else:
            upcoming = tier
            break

    if upcoming is None:
        return LevelProgress(
            level=current.level,
            name=current.name,
            xp_total=xp,
            current_level_xp=current.min_xp,
            next_level_xp=None,
            xp_into_level=xp - current.min_xp,
            xp_to_next=None,
            progress_percentage=100,
            is_max_level=True,
        )

    span = upcoming.min_xp - current.min_xp
    into_level = xp - current.min_xp
    percentage = round((into_level / span) * 100) if span > 0 else 0

    return LevelProgress(
        level=current.level,
        name=current.name,
        xp_total=xp,
        current_level_xp=current.min_xp,
        next_level_xp=upcoming.min_xp,
        xp_into_level=into_level,
        xp_to_next=upcoming.min_xp - xp,
        progress_percentage=min(max(percentage, 0), 100),
        is_max_level=False,
    )
