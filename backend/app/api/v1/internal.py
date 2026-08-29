"""Router de endpoints internos (EPIC 14 — Predição de evasão).

Protegido por API key de serviço (`Depends(verify_internal_api_key)`), nunca
por JWT de usuário — quem chama aqui é o próprio job agendado (ou uma chamada
manual de operação), não um coordenador logado no app.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import verify_internal_api_key
from app.core.database import get_db
from app.core.exceptions import BadRequestException
from app.core.seed import seed as run_seed
from app.schemas.candidate_reset import CandidateResetRequest, CandidateResetSummary
from app.schemas.reminder import ReminderCheckSummary
from app.schemas.response import ApiResponse
from app.schemas.risk import RecomputeSummary
from app.schemas.seed import SeedSummary
from app.services import candidate_reset_service, reminder_service, risk_service

router = APIRouter(prefix="/internal", tags=["Interno"])


@router.post(
    "/risk/recompute",
    response_model=ApiResponse[RecomputeSummary],
    summary="Recalcula o score de risco de todos os candidatos ativos",
    dependencies=[Depends(verify_internal_api_key)],
)
async def recompute_risk(db: AsyncSession = Depends(get_db)) -> ApiResponse[RecomputeSummary]:
    """Dispara manualmente o mesmo recálculo que o job agendado executa periodicamente."""
    data = await risk_service.recompute_all(db)
    return ApiResponse(success=True, message="Recálculo de risco concluído.", data=data)


@router.post(
    "/reminders/check",
    response_model=ApiResponse[ReminderCheckSummary],
    summary="Verifica e dispara os lembretes automáticos pendentes",
    dependencies=[Depends(verify_internal_api_key)],
)
async def check_reminders(db: AsyncSession = Depends(get_db)) -> ApiResponse[ReminderCheckSummary]:
    """Dispara manualmente a mesma verificação que o job agendado executa periodicamente."""
    data = await reminder_service.check_and_send_reminders(db)
    return ApiResponse(success=True, message="Verificação de lembretes concluída.", data=data)


@router.post(
    "/seed",
    response_model=ApiResponse[SeedSummary],
    summary="Semeia os catálogos (jornada, missões, conquistas, questões de simulado...)",
    dependencies=[Depends(verify_internal_api_key)],
)
async def trigger_seed() -> ApiResponse[SeedSummary]:
    """Mesmo `python -m app.core.seed`, disparável em produção via API.

    Idempotente por chave natural de cada catálogo (ver `app.core.seed.seed`)
    — nunca duplica um registro já existente, só insere o que for novo. Abre
    a própria sessão de banco (não usa `Depends(get_db)`): é o mesmo `seed()`
    chamado pelo script de linha de comando, sem nenhuma lógica duplicada.
    """
    result = await run_seed()
    data = SeedSummary(
        journey_steps_created=result.journey_steps_created,
        missions_created=result.missions_created,
        achievements_created=result.achievements_created,
        events_created=result.events_created,
        rewards_created=result.rewards_created,
        cohorts_created=result.cohorts_created,
        profiles_assigned_to_cohort=result.profiles_assigned_to_cohort,
        simulado_questions_created=result.simulado_questions_created,
    )
    return ApiResponse(success=True, message="Seed concluído.", data=data)


@router.post(
    "/candidates/reset",
    response_model=ApiResponse[CandidateResetSummary],
    summary="Reseta uma conta de candidato de teste para o estado de recém-cadastrado",
    dependencies=[Depends(verify_internal_api_key)],
)
async def reset_candidate(
    payload: CandidateResetRequest, db: AsyncSession = Depends(get_db)
) -> ApiResponse[CandidateResetSummary]:
    """Apaga progresso/jornada/gamificação de uma conta de teste e recria do
    zero (mesmo estado de um cadastro novo) — usado antes de demonstrações.

    Irreversível (DELETE real em cascata): exige `confirm: true` no corpo.
    """
    if not payload.confirm:
        raise BadRequestException(
            "Confirme explicitamente (`confirm: true`) para prosseguir — ação irreversível."
        )
    data = await candidate_reset_service.reset_candidate_to_zero(
        db, payload.email, also_remove_guardian_emails=payload.also_remove_guardian_emails
    )
    return ApiResponse(
        success=True, message="Conta resetada para o estado de recém-cadastrado.", data=data
    )
