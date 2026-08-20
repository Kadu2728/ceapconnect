"""Model SQLAlchemy da materialized view `cohort_xp_standing` (Fase 4 — otimizações medidas).

Pré-calcula, por candidato, quantos colegas de coorte têm XP menor ou igual ao
dele — a mesma conta que `CohortStatsRepository.xp_standing` fazia via
agregação ao vivo (`COUNT(*) FILTER (...)` sobre toda a coorte) em **toda**
carga do Dashboard, o endpoint mais chamado da aplicação. O refresh periódico
(`app.core.scheduler`) troca N agregações por request por 1 leitura indexada
+ 1 recálculo em lote.

**Somente leitura.** Nunca insira/atualize via ORM — o conteúdo é gerido
inteiramente por `REFRESH MATERIALIZED VIEW` (a `CREATE MATERIALIZED VIEW`
está na migration, não aqui). `candidate_profile_id` é declarado como chave
primária só para o SQLAlchemy conseguir mapear a classe — a view em si não
tem constraint de PK.
"""

import uuid

from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CohortXpStanding(Base):
    """Linha pré-calculada de `(total, at_or_below)` de XP para um candidato."""

    __tablename__ = "cohort_xp_standing"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    cohort_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True))
    total: Mapped[int] = mapped_column(Integer)
    at_or_below: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return (
            f"<CohortXpStanding candidate_profile_id={self.candidate_profile_id} "
            f"total={self.total} at_or_below={self.at_or_below}>"
        )
