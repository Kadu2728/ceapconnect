"""Regra de negócio de bootstrap do perfil de gamificação (EPIC 03 — Dashboard).

Encapsula tudo que precisa acontecer quando um novo candidato é registrado,
além da criação do `User` em si (EPIC 02): criar o `CandidateProfile` e
semear o progresso `pending` de cada missão do catálogo, para que o
Dashboard sempre tenha dados reais para exibir.

Chamado por `app.services.auth_service.register_user` — nunca por um
router diretamente.
"""

import uuid
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.repositories.journey_step_repository import JourneyStepRepository
from app.repositories.mission_repository import MissionProgressRepository, MissionRepository

# A jornada nasce com a Inscrição (step 1) já concluída pelo próprio cadastro
# — o candidato começa, portanto, na segunda etapa do catálogo.
_INITIAL_STEP_ORDER = 2


async def get_profile_or_raise(db: AsyncSession, user: User) -> CandidateProfile:
    """Resolve o `CandidateProfile` do usuário autenticado ou levanta 404.

    Helper compartilhado pelos services que operam sobre o perfil de
    gamificação (missões, conquistas, eventos). Em condições normais o perfil
    sempre existe — todo `User` ganha um no registro.
    """
    profile = await CandidateProfileRepository(db).get_by_user_id(user.id)
    if profile is None:
        raise NotFoundException("Perfil do candidato não encontrado.")
    return profile


async def bootstrap_new_candidate(db: AsyncSession, user_id: uuid.UUID) -> CandidateProfile:
    """Cria o `CandidateProfile` e o progresso inicial de missões de um candidato novo.

    Não commita: faz parte da mesma transação de `auth_service.register_user`,
    que decide o limite final (commit único, atômico com a criação do `User`).
    """
    initial_step_key = await _resolve_initial_journey_step_key(db)
    exam_date = date.today() + timedelta(days=settings.default_exam_offset_days)
    # A entrevista com o responsável (3ª etapa do processo seletivo real)
    # acontece depois da prova — mesmo racional provisório de offset fixo.
    interview_date = exam_date + timedelta(days=settings.interview_offset_days)

    profile = await CandidateProfileRepository(db).create(
        user_id=user_id,
        current_journey_step_key=initial_step_key,
        exam_date=exam_date,
        interview_date=interview_date,
    )

    missions = await MissionRepository(db).list_all()
    await MissionProgressRepository(db).bulk_create_pending(
        candidate_profile_id=profile.id,
        mission_ids=[mission.id for mission in missions],
    )

    return profile


async def _resolve_initial_journey_step_key(db: AsyncSession) -> str:
    """Resolve a chave da etapa inicial do candidato (2ª etapa do catálogo).

    Faz fallback para a 1ª etapa caso a 2ª ainda não exista (defensivo), e
    levanta um erro de negócio claro caso o catálogo de jornada esteja
    completamente vazio — cenário que só deve ocorrer se o seed
    (`python -m app.core.seed`) ainda não tiver sido executado.
    """
    repo = JourneyStepRepository(db)
    step = await repo.get_by_order(_INITIAL_STEP_ORDER) or await repo.get_by_order(1)
    if step is None:
        raise BadRequestException(
            "Catálogo de etapas da jornada não configurado. "
            "Rode o seed (`python -m app.core.seed`) antes de registrar candidatos."
        )
    return step.key
