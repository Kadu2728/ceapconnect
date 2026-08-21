"""Router do Console de Intervenção (EPIC 14 — Predição de evasão).

Rotas protegidas por `Depends(get_cohort_scope)` — coordenador vê apenas as
próprias coortes, admin vê todas (ver `app.core.rbac.CohortScope`). A regra de
negócio vive em `app.services.risk_service` — o router apenas orquestra e
envelopa.

**Nunca** exposto a candidatos: nenhuma rota aqui é acessível com
`Depends(get_current_user)` puro — todas exigem `get_cohort_scope`, que por
sua vez exige `get_current_coordinator`.
"""

import asyncio
import logging
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CohortScope, get_cohort_scope
from app.core.database import AsyncSessionLocal, get_db
from app.core.risk_scoring import RiskTier
from app.schemas.response import ApiResponse
from app.schemas.risk import (
    CandidateRiskDetail,
    CandidateStatusItem,
    CandidateStatusUpdateRequest,
    InterventionCreateRequest,
    InterventionItem,
    RiskQueueResponse,
)
from app.services import risk_service

router = APIRouter(tags=["Predição de Evasão"])
logger = logging.getLogger("ceap_connect.risk_stream")

# Intervalo de repolling do SSE (Fase 3 — moat: fila em tempo real).
#
# Poll-e-compare em vez de push-on-write: o processo web roda com múltiplos
# workers (UVICORN_WORKERS, ver Dockerfile) sem broker de pub/sub obrigatório
# (Redis é opcional, ver app.core.cache) — um evento publicado no worker A
# nunca chegaria a um cliente SSE conectado no worker B. Poll-e-compare
# funciona identicamente em qualquer número de workers, sem depender de
# nenhuma infra nova. 8s é impercetível para o caso de uso (coordenador
# olhando a fila), bem abaixo do que justificaria a complexidade de um
# broker.
_STREAM_POLL_INTERVAL_SECONDS = 8


@router.get(
    "/admin/risk/queue",
    response_model=ApiResponse[RiskQueueResponse],
    summary="Fila priorizada de candidatos em risco de evasão",
)
async def get_risk_queue(
    cohort_id: uuid.UUID | None = Query(default=None),
    tier: RiskTier | None = Query(default=None),
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RiskQueueResponse]:
    """Candidatos ordenados do maior para o menor risco, dentro do escopo do usuário."""
    data = await risk_service.get_queue(db, scope, cohort_id=cohort_id, tier=tier)
    return ApiResponse(success=True, message="Fila de risco recuperada com sucesso.", data=data)


@router.get(
    "/admin/risk/queue/stream",
    summary="Fila de risco em tempo real (Server-Sent Events)",
)
async def stream_risk_queue(
    cohort_id: uuid.UUID | None = Query(default=None),
    tier: RiskTier | None = Query(default=None),
    scope: CohortScope = Depends(get_cohort_scope),
) -> StreamingResponse:
    """Empurra a fila de risco sempre que ela mudar — sem o coordenador precisar dar F5.

    Autenticação via header `Authorization` normal (não `EventSource`, que não
    suporta headers customizados) — o frontend consome isto com `fetch` +
    leitura de stream, não com a API `EventSource` do navegador.
    """
    return StreamingResponse(
        _risk_queue_event_stream(scope, cohort_id, tier),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # Desliga buffering de proxies reversos (nginx e afins) que
            # segurariam os chunks até acumular um bloco maior, atrasando a
            # entrega — sem efeito quando não há esse proxy na frente, então é
            # seguro deixar sempre ligado.
            "X-Accel-Buffering": "no",
        },
    )


async def _risk_queue_event_stream(
    scope: CohortScope,
    cohort_id: uuid.UUID | None,
    tier: RiskTier | None,
) -> AsyncGenerator[str]:
    """Gerador do SSE: reconsulta a fila a cada poucos segundos, só emite quando muda.

    Abre uma sessão de banco nova a cada iteração (nunca reaproveita a sessão
    de um request comum) — um SSE fica aberto por minutos, e segurar uma
    conexão do pool ociosa durante todo esse tempo é exatamente o tipo de
    pressão em conexões que a migração para o endpoint pooled da Neon
    (Fase 4) tenta evitar.
    """
    last_payload: str | None = None
    while True:
        try:
            async with AsyncSessionLocal() as db:
                data = await risk_service.get_queue(db, scope, cohort_id=cohort_id, tier=tier)
            payload = data.model_dump_json()
        except Exception:  # noqa: BLE001 — o stream nunca pode derrubar o worker
            logger.exception("Falha ao atualizar a fila de risco via SSE")
            await asyncio.sleep(_STREAM_POLL_INTERVAL_SECONDS)
            continue

        if payload != last_payload:
            last_payload = payload
            yield f"data: {payload}\n\n"
        else:
            # Comentário SSE (linha começando com ":"): mantém a conexão viva
            # através de proxies/load balancers que fecham streams ociosos,
            # sem reenviar dado que não mudou.
            yield ": heartbeat\n\n"

        await asyncio.sleep(_STREAM_POLL_INTERVAL_SECONDS)


@router.get(
    "/admin/candidates/{candidate_profile_id}/risk",
    response_model=ApiResponse[CandidateRiskDetail],
    summary="Detalhe de risco de um candidato",
)
async def get_candidate_risk(
    candidate_profile_id: uuid.UUID,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CandidateRiskDetail]:
    """Score, fatores explicativos, timeline de atividade e histórico de intervenções."""
    data = await risk_service.get_candidate_risk(db, scope, candidate_profile_id)
    return ApiResponse(
        success=True, message="Risco do candidato recuperado com sucesso.", data=data
    )


@router.patch(
    "/admin/candidates/{candidate_profile_id}/status",
    response_model=ApiResponse[CandidateStatusItem],
    summary="Registra o outcome real do candidato (rótulo usado no backtest do modelo de risco)",
)
async def update_candidate_status(
    candidate_profile_id: uuid.UUID,
    payload: CandidateStatusUpdateRequest,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CandidateStatusItem]:
    """Marca aprovado/evadido/desistente — sempre uma ação manual do coordenador.

    A partir daqui o candidato sai do recálculo periódico de risco; o último
    score calculado fica congelado como o valor comparado ao outcome real.
    """
    profile = await risk_service.update_candidate_status(
        db, scope, candidate_profile_id, payload.status
    )
    data = CandidateStatusItem(status=profile.status, status_changed_at=profile.status_changed_at)
    return ApiResponse(success=True, message="Status do candidato atualizado.", data=data)


@router.post(
    "/admin/interventions",
    response_model=ApiResponse[InterventionItem],
    status_code=201,
    summary="Registra uma intervenção com um candidato em risco",
)
async def create_intervention(
    payload: InterventionCreateRequest,
    scope: CohortScope = Depends(get_cohort_scope),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[InterventionItem]:
    """Registra o contato (ligar/WhatsApp/outro) e o resultado imediato."""
    data = await risk_service.create_intervention(db, scope, payload)
    return ApiResponse(success=True, message="Intervenção registrada com sucesso.", data=data)
