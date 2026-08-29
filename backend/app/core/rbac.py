"""RBAC com escopo de coorte (EPIC 14) — tipos e regras puras, sem FastAPI.

Vive em `core` (não em `api/v1/deps.py`) para que qualquer service possa
depender do conceito de escopo sem depender da camada HTTP — `deps.py` importa
daqui e só adiciona a fiação de `Depends`.
"""

import uuid
from dataclasses import dataclass

from app.models.user import ROLE_ADMIN, User


def is_admin(user: User) -> bool:
    """Indica se o usuário é administrador.

    Aceita tanto o papel novo (`role == "admin"`) quanto o booleano legado
    (`is_admin`), para a migração de RBAC não quebrar contas já promovidas.
    """
    return user.role == ROLE_ADMIN or user.is_admin


@dataclass(frozen=True)
class CohortScope:
    """Escopo de coortes que o usuário atual pode enxergar.

    `cohort_ids is None` = irrestrito (admin). Caso contrário, a lista é o
    conjunto exato de coortes permitidas — e uma lista **vazia** significa
    "nenhum candidato visível" (coordenador ainda sem coorte atribuída), nunca
    "todos". O filtro deve ser aplicado na query do repositório, jamais em
    memória: assim um coordenador não consegue sequer enumerar candidatos de
    outra coorte.
    """

    user: User
    cohort_ids: list[uuid.UUID] | None

    @property
    def is_unrestricted(self) -> bool:
        """True quando o usuário enxerga todas as coortes (admin)."""
        return self.cohort_ids is None

    def allows(self, cohort_id: uuid.UUID | None) -> bool:
        """Indica se uma coorte específica está dentro do escopo."""
        if self.is_unrestricted:
            return True
        if cohort_id is None:
            # Candidato sem coorte só é visível para admin.
            return False
        return cohort_id in (self.cohort_ids or [])


@dataclass(frozen=True)
class GuardianScope:
    """Escopo de candidatos que um responsável autenticado pode enxergar.

    Diferente de `CohortScope`, nunca é irrestrito — não existe "responsável
    admin" que vê todo mundo. `candidate_profile_ids` é sempre uma lista
    concreta (pode ser vazia: responsável sem nenhum vínculo autorizado
    ainda, ex.: só tem vínculos `pending`). Resolvida por
    `GuardianCandidateLinkRepository.list_authorized_candidate_ids` — já
    filtrado por `consent_status`, nunca em memória.
    """

    user: User
    candidate_profile_ids: list[uuid.UUID]

    def allows(self, candidate_profile_id: uuid.UUID) -> bool:
        return candidate_profile_id in self.candidate_profile_ids
