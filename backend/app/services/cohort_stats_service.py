"""Percentil de engajamento na coorte, sem ranking nominal (EPIC 20).

Mostrar ao candidato que ele está "entre os 20% mais engajados da turma"
motiva; mostrar um placar com nomes estigmatiza quem está no fim dele — e o
público aqui são adolescentes em situação de vulnerabilidade, exatamente os
que mais evadem quando se sentem expostos. Por isso esta feature devolve
**apenas uma faixa agregada**, nunca posição exata nem identidade de ninguém.

Três salvaguardas deliberadas:

1. **Nunca posição nominal.** A API não tem endpoint de leaderboard; o
   repositório só sabe contar, não listar candidatos.
2. **Coorte pequena não recebe percentil.** Abaixo de `_MIN_COHORT_SIZE`, "top
   20%" seria praticamente identificável ("só tem 3 pessoas na turma") — nesses
   casos devolvemos `None` e a UI simplesmente não mostra o card.
3. **Só faixas positivas.** Arredondamos para faixas amplas (top 10/25/50%) e
   nunca comunicamos a metade de baixo como "você está entre os piores": quem
   não está no top 50% recebe uma mensagem de progresso pessoal, não de
   comparação.
"""

from typing import Final

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import CandidateProfile
from app.repositories.cohort_stats_repository import CohortStatsRepository
from app.schemas.dashboard import CohortStanding

# Abaixo disso, qualquer faixa percentual é identificável na prática.
_MIN_COHORT_SIZE: Final = 5

# Faixas comunicáveis, da mais forte para a mais fraca.
_TOP_BANDS: Final = (10, 25, 50)


async def build_cohort_standing(
    db: AsyncSession, profile: CandidateProfile
) -> CohortStanding | None:
    """Calcula a faixa de engajamento do candidato dentro da coorte dele.

    Retorna `None` (a UI omite o card) quando o candidato ainda não tem coorte,
    quando a turma é pequena demais para anonimato, ou quando ele ainda não
    pontuou — nesses casos comparar não informa nada e só pode desmotivar.
    """
    if profile.cohort_id is None or profile.xp_total <= 0:
        return None

    standing = await CohortStatsRepository(db).xp_standing(candidate_profile_id=profile.id)
    if standing is None:
        return None
    total, at_or_below = standing
    if total < _MIN_COHORT_SIZE:
        return None

    # Percentil calculado em Python, nunca no SQL — mesma razão do
    # `admin_service`: divisão por zero e arredondamento são regra de negócio.
    percentile = round((at_or_below / total) * 100)
    top_percent = _resolve_top_band(percentile)

    return CohortStanding(
        cohort_size=total,
        top_percent=top_percent,
        message=_build_message(top_percent),
    )


def _resolve_top_band(percentile: int) -> int | None:
    """Converte o percentil na faixa ampla mais forte que o candidato alcança."""
    for band in _TOP_BANDS:
        if percentile >= 100 - band:
            return band
    return None


def _build_message(top_percent: int | None) -> str:
    """Mensagem sempre construtiva — nunca comunica "metade de baixo"."""
    if top_percent is None:
        return "Cada missão concluída te aproxima do topo da sua turma. Continue!"
    return f"Você está entre os {top_percent}% mais engajados da sua turma."
