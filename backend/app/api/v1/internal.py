"""Router de endpoints internos (EPIC 14 — Predição de evasão).

Protegido por API key de serviço (`Depends(verify_internal_api_key)`), nunca
por JWT de usuário — quem chama aqui é o próprio job agendado (ou uma chamada
manual de operação), não um coordenador logado no app.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import verify_internal_api_key
from app.core.database import get_db
from app.schemas.reminder import ReminderCheckSummary
from app.schemas.response import ApiResponse
from app.schemas.risk import RecomputeSummary
from app.services import reminder_service, risk_service

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
